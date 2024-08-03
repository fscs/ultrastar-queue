import os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from decouple import config
from src.database.models import UltrastarSong
from src.database.controller import init_db, clean_db, add_song_if_not_in_db, get_session
from src.queue.routes import queue_router
from src.songs.routes import song_router
from src.auth.routes import auth_router
from src.admin.routes import admin_router
from src.ultrastar_file_parser.parser import UltrastarFileParser
from src.songs.schemas import UltrastarSongBase, UltrastarSongConverter
from sqlmodel.ext.asyncio.session import AsyncSession


async def populate_database():
    path = config("PATH_TO_ULTRASTAR_SONG_DIR")
    files = UltrastarFileParser.get_song_file_paths(path)
    for file_path in files:
        try:
            attr_dict = UltrastarFileParser.parse_file_for_ultrastar_song_attributes(file_path)
        except ValueError as e:
            print(f"Not an ultrastar file: {file_path}")
            print(e)
            continue
        audio_duration = UltrastarFileParser.get_audio_duration(os.path.dirname(file_path), attr_dict["audio"])
        attr_dict["audio_duration_in_seconds"] = audio_duration
        song_converter = UltrastarSongConverter(**attr_dict)
        song_base: UltrastarSongBase = UltrastarSongBase(
            title=song_converter.title,
            artist=song_converter.artist,
            lyrics=song_converter.lyrics
        )

        # https://stackoverflow.com/questions/75150942/how-to-get-a-session-from-async-session-generator-fastapi-sqlalchemy
        generator = get_session()
        session: AsyncSession = (await anext(generator))
        song = await add_song_if_not_in_db(session, UltrastarSong(**song_base.dict()))
        try:
            await anext(generator)
        except StopAsyncIteration:
            pass
        if song:
            print(f"{song.title} by {song.artist} added to db")
        else:
            print(f"{song_base.title} by {song_base.artist} already in db")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    try:
        await populate_database()
    except FileNotFoundError as e:
        if e.args[0] == "Could not find path: ":
            raise FileNotFoundError("Please make sure, that a path to ultrastar files is configured in .env")
        else:
            raise e
    yield
    await clean_db()

app = FastAPI(lifespan=lifespan)

app.include_router(queue_router)
app.include_router(song_router)
app.include_router(auth_router)
app.include_router(admin_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
