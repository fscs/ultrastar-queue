from fastapi import APIRouter, Depends, HTTPException, status
from .controller import QueueController
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.controller import is_admin
from src.database.db import get_session
from src.database import controller as db_controller
from src.database.models import UltrastarSong
from .schemas import SongInQueue

queue_router = APIRouter(
    prefix="/queue",
    tags=["queue"],
    dependencies=[],
    responses={404: {"description": "Not found"}}
)

queue_handler = QueueController()


@queue_router.get("/")
async def get_queue():
    return queue_handler.get_queue()


@queue_router.post("/add-song")
async def add_song_to_queue(requested_song: UltrastarSong, singer: str, session: AsyncSession = Depends(get_session)):
    song_in_db = await db_controller.get_song_by_id(session, requested_song.id)
    if not song_in_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song not in database")
    elif (requested_song.title != song_in_db.title) or (requested_song.artist != song_in_db.artist):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Songdata not matching")
    song_in_queue = SongInQueue(song=song_in_db, singer=singer)
    queue_handler.add_song_at_end(song_in_queue)
    return song_in_queue


@queue_router.put("/check-first-song", dependencies=[Depends(is_admin)])
async def check_first_song_in_queue():
    try:
        checked = queue_handler.mark_first_song_as_processed()
    except IndexError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Queue is empty")
    return {"checked": checked}


@queue_router.delete("/remove-song", dependencies=[Depends(is_admin)])
async def remove_song_from_queue(index: int):
    try:
        removed = queue_handler.remove_song_by_index(index)
    except IndexError:
        raise
    return {"deleted": removed}


@queue_router.delete("/clear_queue", dependencies=[Depends(is_admin)])
async def clear_queue():
    queue_handler.clear_queue()
    return {"message": "Queue cleared"}
