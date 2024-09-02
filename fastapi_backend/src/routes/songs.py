from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from ..app import db_controller
from ..exceptions.songs import (EmptySonglistHTTPException,
                                NoMatchingSongHTTPException,
                                SongIdNotMatchingHTTPException)
from ..models.songs import UltrastarSong
from ..services.session import SessionService

song_router = APIRouter(
    prefix="/songs",
    tags=["songs"],
    dependencies=[],
    responses={404: {"description": "Not found"}}
)


@song_router.get("/", response_model=list[UltrastarSong])
async def get_songs(
        session: AsyncSession = Depends(db_controller.get_session)
) -> list[UltrastarSong]:
    songs = await SessionService.get_songs(session)
    if not songs:
        raise EmptySonglistHTTPException()
    return songs


@song_router.get(path="/get-songs-by-criteria")
async def get_songs_by_criteria(
        title: str | None = None,
        artist: str | None = None,
        session: AsyncSession = Depends(db_controller.get_session)
) -> list[UltrastarSong]:
    songs = await SessionService.get_songs_by_criteria(session, title, artist)
    if not songs:
        raise NoMatchingSongHTTPException()
    return songs


@song_router.get("/{song_id}")
async def get_song_by_id(
        song_id: int,
        session: AsyncSession = Depends(db_controller.get_session)
) -> UltrastarSong:
    song = await SessionService.get_song_by_id(session, song_id)
    if song is None:
        raise SongIdNotMatchingHTTPException()
    return song
