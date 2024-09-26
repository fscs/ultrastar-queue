import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel.ext.asyncio.session import AsyncSession

from .auth.crud import add_user, get_user_by_username
from .auth.models import User
from .config import settings
from .dependencies import get_async_session
from .queue.service import QueueService
from .songs.crud import add_song_if_not_in_db
from .songs.models import UltrastarSong
from .songs.schemas import UltrastarSongBase, UltrastarSongConverter
from ..logging.controller import setup_logging, get_db_logger
from ..ultrastar_file_parser import UltrastarFileParser
from ..ultrastar_file_parser.exceptions import UltrastarMatchingError


async def populate_database() -> None:
    path = settings.PATH_TO_ULTRASTAR_SONG_DIR
    file_paths = UltrastarFileParser.get_song_file_paths(path)
    for file_path in file_paths:
        try:
            attr_dict = UltrastarFileParser.parse_file_for_ultrastar_song_attributes(file_path)
        except UltrastarMatchingError as e:
            db_logger.error(e.args[0] + f"Probably not an ultrastar file: {file_path}\n")
            continue
        song_converter = UltrastarSongConverter(**attr_dict)
        try:
            song_converter.set_audio_duration(os.path.dirname(file_path))
        except RuntimeError as e:
            db_logger.error(e.args[0])
        except FileNotFoundError as e:
            db_logger.error(e.args[0])
        song_base: UltrastarSongBase = UltrastarSongBase(**song_converter.model_dump())

        song = None
        # https://stackoverflow.com/questions/56161595/how-to-use-async-for-in-python
        async for session in get_async_session():
            song = await add_song_if_not_in_db(session, UltrastarSong(**song_base.dict()))
        if song:
            db_logger.info(f"{song.title} by {song.artist} added to db")
        else:
            db_logger.info(f"{song_base.title} by {song_base.artist} already in db")


async def add_users_to_db() -> None:
    from src.app.auth.utils import get_password_hash

    hashed_password = get_password_hash(settings.ADMIN_PASSWORD)
    user1 = User(username=settings.ADMIN_USERNAME, is_admin=True, hashed_password=hashed_password)
    async for session in get_async_session():
        if not await get_user_by_username(session, user1.username):
            await add_user(session, user1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await populate_database()
        await add_users_to_db()
    except FileNotFoundError as e:
        if e.args[0] == "Could not find path: ":
            raise FileNotFoundError("Please make sure, that a path to ultrastar files is configured in .env")
        else:
            raise e
    yield


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan, docs_url=settings.SWAGGER_UI_URL, redoc_url=settings.REDOC_URL)

    from src.app.auth.routes import auth_router
    from src.app.queue.routes import queue_router
    from src.app.songs.routes import song_router
    from src.app.admin.routes import admin_router

    app.include_router(queue_router)
    app.include_router(song_router)
    app.include_router(auth_router)
    app.include_router(admin_router)

    origins = [
        f"http://{settings.FRONTEND_HOST}:{settings.FRONTEND_PORT}",
        f"https://{settings.FRONTEND_HOST}:{settings.FRONTEND_PORT}"
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
