from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.controller import get_session
from src.database import controller as db_controller
from src.database.models import UltrastarSong
from src.auth.controller import is_admin
from .schemas import UltrastarSongBase
from .exceptions import (EmptySonglistHTTPException,
                         NoMatchingSongHTTPException,
                         SongIdNotMatchingHTTPException)

song_router = APIRouter(
    prefix="/songs",
    tags=["songs"],
    dependencies=[],
    responses={404: {"description": "Not found"}}
)


@song_router.get("/")
async def get_songs(
        session: AsyncSession = Depends(get_session)
        ) -> list[UltrastarSong]:
    songs = await db_controller.get_songs(session)
    if not songs:
        raise EmptySonglistHTTPException()
    return songs


@song_router.get(path="/get-songs-by-criteria")
async def get_songs_by_criteria(
        title: str | None = None,
        artist: str | None = None,
        session: AsyncSession = Depends(get_session)
        ) -> list[UltrastarSong]:
    songs = await db_controller.get_songs_by_criteria(session, title, artist)
    if not songs:
        raise NoMatchingSongHTTPException()
    return songs


@song_router.get("/{song_id}")
async def get_song_by_id(
        song_id: int,
        session: AsyncSession = Depends(get_session)
        ) -> UltrastarSong:
    song = await db_controller.get_song_by_id(session, song_id)
    if song is None:
        raise SongIdNotMatchingHTTPException()
    return song


@song_router.post("/create-song", dependencies=[Depends(is_admin)], status_code=status.HTTP_201_CREATED)
async def create_song(
        song_data: UltrastarSongBase,
        session: AsyncSession = Depends(get_session)
        ) -> UltrastarSong:
    song = UltrastarSong(title=song_data.title, artist=song_data.artist, lyrics=song_data.lyrics)
    song = await db_controller.add_song(session=session, song=song)
    return song
