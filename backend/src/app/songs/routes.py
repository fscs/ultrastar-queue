from fastapi import APIRouter, status

from . import crud
from .exceptions import (EmptySonglistHTTPException,
                         NoMatchingSongHTTPException)
from .models import UltrastarSong
from ..dependencies import AsyncSessionDep

song_router = APIRouter(
    prefix="/songs",
    tags=["songs"],
    dependencies=[],
    responses={404: {"description": "Not found"}}
)


@song_router.get("/", response_model=list[UltrastarSong])
async def get_songs(session: AsyncSessionDep) -> list[UltrastarSong]:
    songs = await crud.get_songs(session)
    if not songs:
        raise EmptySonglistHTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Songlist is empty")
    return songs


@song_router.get("/get-songs-by-criteria")
async def get_songs_by_criteria(
        session: AsyncSessionDep,
        title: str | None = None,
        artist: str | None = None
) -> list[UltrastarSong]:
    songs = await crud.get_songs_by_criteria(session, title, artist)
    if not songs:
        raise NoMatchingSongHTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                          detail="Could not find songs with provided criteria")
    return songs


@song_router.get("/{song_id}")
async def get_song_by_id(
        session: AsyncSessionDep,
        song_id: int
) -> UltrastarSong:
    song = await crud.get_song_by_id(session, song_id)
    if song is None:
        raise NoMatchingSongHTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                          detail="Requested song id cannot be found in database")
    return song
