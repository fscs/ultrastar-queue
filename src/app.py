import os
from contextlib import asynccontextmanager

from decouple import config
from fastapi import FastAPI
from sqlmodel.ext.asyncio.session import AsyncSession

from src.database import DBController, SessionController
from src.database.models import UltrastarSong
from src.songs.schemas import UltrastarSongBase, UltrastarSongConverter
from src.ultrastar_file_parser.parser import UltrastarFileParser


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
        song_converter = UltrastarSongConverter(**attr_dict)
        song_converter.set_audio_duration(os.path.dirname(file_path))
        song_base: UltrastarSongBase = UltrastarSongBase(**song_converter.model_dump())

        # https://stackoverflow.com/questions/75150942/how-to-get-a-session-from-async-session-generator-fastapi-sqlalchemy
        generator = db_controller.get_session()
        session: AsyncSession = (await anext(generator))
        song = await SessionController.add_song_if_not_in_db(session, UltrastarSong(**song_base.dict()))
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
    await db_controller.init_db()
    try:
        await populate_database()
    except FileNotFoundError as e:
        if e.args[0] == "Could not find path: ":
            raise FileNotFoundError("Please make sure, that a path to ultrastar files is configured in .env")
        else:
            raise e
    yield
    await db_controller.clean_db()


def setup_routers():
    from src.admin.routes import admin_router
    from src.auth.routes import auth_router
    from src.queue.routes import queue_router
    from src.songs.routes import song_router

    app.include_router(queue_router)
    app.include_router(song_router)
    app.include_router(auth_router)
    app.include_router(admin_router)


db_controller = DBController(config("DATABASE_URL"))
app = FastAPI(lifespan=lifespan)
setup_routers()


@app.get("/")
async def root():
    return {"message": "Hello World"}
