from fastapi import APIRouter, Depends
from .controller import QueueController
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.controller import is_admin
from src.database.controller import get_session
from src.database import controller as db_controller
from src.database.models import UltrastarSong
from .schemas import SongInQueue
from .exceptions import *

queue_router = APIRouter(
    prefix="/queue",
    tags=["queue"],
    dependencies=[],
    responses={404: {"description": "Not found"}}
)

queue_controller = QueueController()


@queue_router.get("/")
async def get_queue():
    return queue_controller.get_queue()


@queue_router.post("/add-song", status_code=status.HTTP_201_CREATED)
async def add_song_to_queue(requested_song: UltrastarSong, singer: str, session: AsyncSession = Depends(get_session)):
    song_in_db = await db_controller.get_song_by_id(session, requested_song.id)
    if not song_in_db:
        raise SongNotInDatabaseHTTPException()
    elif (requested_song.title != song_in_db.title) or (requested_song.artist != song_in_db.artist):
        raise MismatchingSongDataHTTPException()
    song_in_queue = SongInQueue(song=song_in_db, singer=singer)
    try:
        queue_controller.add_song_at_end(song_in_queue)
    except QueueClosedError as err:
        raise QueueClosedHTTPException(detail=err.msg)
    return song_in_queue


@queue_router.put("/check-first-song", dependencies=[Depends(is_admin)])
async def check_first_song_in_queue():
    try:
        checked = queue_controller.mark_first_song_as_processed()
    except QueueEmptyError as err:
        raise QueueEmptyHTTPException(detail=err.msg)
    return {"checked": checked}


@queue_router.delete("/remove-song", dependencies=[Depends(is_admin)])
async def remove_song_from_queue(index: int):
    try:
        removed = queue_controller.remove_song_by_index(index)
    except QueueIndexError as err:
        raise QueueIndexHTTPException(detail=err.msg)
    return {"deleted": removed}


@queue_router.delete("/clear-queue", dependencies=[Depends(is_admin)])
async def clear_queue():
    queue_controller.clear_queue()
    return {"message": "Queue cleared"}
