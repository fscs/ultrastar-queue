from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.db import get_session
from src.database import controller as db_controller
from src.database.models import UltrastarSong
from src.auth.controller import is_admin
from .schemas import UltrastarSongBase

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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Songlist is empty")
    return songs


@song_router.get("/{song_id}")
async def get_song(
        song_id: int,
        session: AsyncSession = Depends(get_session)
        ) -> UltrastarSong:
    song = await db_controller.get_song_by_id(session, song_id)
    if song is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song_id not found")
    return song


# currently broken
@song_router.get("/get-songs-by-criteria")
async def get_songs_by_criteria(
        title: str | None = None,
        artist: str | None = None,
        session: AsyncSession = Depends(get_session)
        ) -> list[UltrastarSong]:
    songs = await db_controller.get_songs_by_criteria(session, title, artist)
    if not songs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Could not find songs with provided criteria")
    return songs


@song_router.post("/create-song", dependencies=[Depends(is_admin)])
async def create_song(
        song_data: UltrastarSongBase,
        session: AsyncSession = Depends(get_session)
        ) -> UltrastarSong:
    song = UltrastarSong(title=song_data.title, artist=song_data.artist, lyrics=song_data.lyrics)
    song = await db_controller.add_song(session=session, song=song)
    return song
