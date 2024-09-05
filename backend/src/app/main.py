import os
from contextlib import asynccontextmanager

from decouple import config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel.ext.asyncio.session import AsyncSession

from backend.src.app.auth.models import User
from backend.src.app.songs.models import UltrastarSong
from backend.src.logging.controller import setup_logging, get_db_logger
from ultrastar_file_parser.parser import UltrastarFileParser
from backend.src.app.dependencies import get_async_session
from backend.src.app.auth.crud import add_user
from backend.src.app.songs.crud import add_song_if_not_in_db
from backend.src.app.database import init_db, clean_db
from backend.src.app.songs.schemas import UltrastarSongBase, UltrastarSongConverter
from backend.src.app.queue.service import QueueService


async def populate_database():
    path = config("PATH_TO_ULTRASTAR_SONG_DIR")
    file_paths = UltrastarFileParser.get_song_file_paths(path)
    for file_path in file_paths:
        try:
            attr_dict = UltrastarFileParser.parse_file_for_ultrastar_song_attributes(file_path)
        except ValueError as e:
            db_logger.error(e.args[0] + f"Probably not an ultrastar file: {file_path}\n")
            continue
        song_converter = UltrastarSongConverter(**attr_dict)
        try:
            song_converter.set_audio_duration(os.path.dirname(file_path))
        except RuntimeError as e:
            db_logger.error(e.args[0])
        song_base: UltrastarSongBase = UltrastarSongBase(**song_converter.model_dump())

        # https://stackoverflow.com/questions/75150942/how-to-get-a-session-from-async-session-generator-fastapi-sqlalchemy
        generator = get_async_session()
        session: AsyncSession = (await anext(generator))
        song = await add_song_if_not_in_db(session, UltrastarSong(**song_base.dict()))
        try:
            await anext(generator)
        except StopAsyncIteration:
            pass
        if song:
            db_logger.info(f"{song.title} by {song.artist} added to db")
        else:
            db_logger.info(f"{song_base.title} by {song_base.artist} already in db")


async def add_users_to_db():
    pw = "$2b$12$VBJFBBwpnnvb9dy.NHdPnOcliuN1pkOPBUMHkfNX8cFJWjl8GlM5O"
    generator = get_async_session()
    session: AsyncSession = (await anext(generator))
    user1 = User(username="bestUser", is_admin=False, hashed_password=pw)
    user2 = User(username="bestAdmin", is_admin=True, hashed_password=pw)
    await add_user(session, user1)
    await add_user(session, user2)
    try:
        await anext(generator)
    except StopAsyncIteration:
        pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    try:
        await populate_database()
        await add_users_to_db()
    except FileNotFoundError as e:
        if e.args[0] == "Could not find path: ":
            raise FileNotFoundError("Please make sure, that a path to ultrastar files is configured in .env")
        else:
            raise e
    yield
    await clean_db()


def create_app():
    app = FastAPI(lifespan=lifespan)

    from backend.src.app.auth.routes import auth_router
    from backend.src.app.queue.routes import queue_router
    from backend.src.app.songs.routes import song_router
    from backend.src.app.admin.routes import admin_router

    app.include_router(queue_router)
    app.include_router(song_router)
    app.include_router(auth_router)
    app.include_router(admin_router)

    origins = [
        f"{config("FRONTEND_SERVER")}:{config("FRONTEND_PORT")}",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


setup_logging()
db_logger = get_db_logger()
queue_service = QueueService()
app = create_app()
