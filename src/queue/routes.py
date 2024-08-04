from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Cookie, Response, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.auth.controller import is_admin
from src.database import controller as db_controller
from src.database.controller import get_session
from src.database.models import UltrastarSong
from .controller import QueueController
from .exceptions import (QueueClosedHTTPException,
                         QueueEmptyError,
                         QueueEmptyHTTPException,
                         QueueIndexError,
                         QueueIndexHTTPException,
                         SongAlreadySungHTTPException,
                         CantSubmitSongHTTPException,
                         SongNotInDatabaseHTTPException,
                         SongAlreadyInQueueHTTPException,
                         MismatchingSongDataHTTPException)
from .schemas import SongInQueue

queue_router = APIRouter(
    prefix="/queue",
    tags=["queue"],
    dependencies=[],
    responses={404: {"description": "Not found"}}
)

queue_controller = QueueController()
TIME_BETWEEN_SONGS = 60


@queue_router.get("/")
async def get_queue():
    return queue_controller.get_queue()


@queue_router.post("/add-song", status_code=status.HTTP_201_CREATED, response_model=SongInQueue)
async def add_song_to_queue(
        response: Response,
        requested_song: UltrastarSong,
        singer: str,
        session: AsyncSession = Depends(get_session),
        last_added: datetime | None = Cookie(None)
):
    if last_added is not None:
        if last_added > (datetime.now() - timedelta(TIME_BETWEEN_SONGS)):
            raise CantSubmitSongHTTPException(
                detail=f"Please wait {TIME_BETWEEN_SONGS} seconds before submitting a new song"
            )

    song_in_db = await db_controller.get_song_by_id(session, requested_song.id)
    if not song_in_db:
        raise SongNotInDatabaseHTTPException()
    elif (requested_song.title != song_in_db.title) or (requested_song.artist != song_in_db.artist):
        raise MismatchingSongDataHTTPException()

    for queue_entry in queue_controller.get_queue():
        if queue_entry.song.__eq__(song_in_db):
            raise SongAlreadyInQueueHTTPException(detail=f"Song {requested_song} is already in queue")

    if song_in_db in queue_controller.get_processed_songs():
        raise SongAlreadySungHTTPException(detail=f"Song {requested_song} has already been sung today")

    song_in_queue = SongInQueue(song=song_in_db, singer=singer)
    if queue_controller.is_queue_open():
        queue_controller.add_song_at_end(song_in_queue)
    else:
        raise QueueClosedHTTPException()

    response.set_cookie("last_added", str(datetime.now()), httponly=True)
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


@queue_router.delete("/clear-processed-songs", dependencies=[Depends(is_admin)])
async def clear_processed_songs():
    queue_controller.clear_processed_songs()
    return {"message": "Processed songs cleared"}


@queue_router.delete("/clear-queue-controller", dependencies=[Depends(is_admin)])
async def clear_queue_controller():
    queue_controller.clear_queue_controller()
    return {"message": "Queue controller cleared"}
