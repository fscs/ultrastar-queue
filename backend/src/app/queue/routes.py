from datetime import datetime

from fastapi import APIRouter, Cookie, Response, status

from .exceptions import (QueueClosedHTTPException,
                         SongAlreadySungHTTPException,
                         SongRecentlySungHTTPException,
                         CantSubmitSongHTTPException,
                         SongNotInDatabaseHTTPException,
                         SongAlreadyInQueueHTTPException)
from .schemas import QueueEntry
from ..dependencies import AsyncSessionDep
from ..main import queue_service
from ..songs.crud import get_song_by_id

queue_router = APIRouter(
    prefix="/queue",
    tags=["queue"],
    dependencies=[],
    responses={404: {"description": "Not found"}}
)


@queue_router.get("/")
def get_queue():
    return queue_service.queue


@queue_router.get("/processed-entries")
def get_processed_entries():
    return queue_service.processed_entries


@queue_router.get("/get-time-until-end-of-queue")
def get_time_until_end_of_queue():
    return queue_service.time_until_end_of_queue()


@queue_router.post("/add-entry", status_code=status.HTTP_201_CREATED, response_model=QueueEntry)
async def add_entry_to_queue(
        session: AsyncSessionDep,
        response: Response,
        requested_song_id: int,
        singer: str,
        last_added: datetime | None = Cookie(None)
):
    if not queue_service.queue_is_open:
        raise QueueClosedHTTPException()

    if last_added is not None:
        if last_added > (datetime.now() - queue_service.time_between_song_submissions):
            raise CantSubmitSongHTTPException(
                detail=f"Please wait {queue_service.time_between_song_submissions} before submitting a new song"
            )

    song = await get_song_by_id(session, requested_song_id)
    if not song:
        raise SongNotInDatabaseHTTPException()

    if queue_service.is_song_in_queue(song):
        raise SongAlreadyInQueueHTTPException(detail=f"Song {song.title} by {song.artist} is "
                                                     f"already in queue")

    if queue_service.has_song_been_sung_max_times(song):
        raise SongAlreadySungHTTPException(detail=f"Song {song.title} by {song.artist} has "
                                                  f"already been sung a few times today. Please choose another one.")

    if not queue_service.will_time_between_songs_have_passed_until_end_of_queue(song):
        raise SongRecentlySungHTTPException(detail=f"Song {song.title} by {song.artist} has "
                                                   "been sung recently. Please choose another one.")

    queue_entry = QueueEntry(song=song, singer=singer)

    queue_service.add_entry_at_end(queue_entry)

    response.set_cookie("last_added", str(datetime.now()), httponly=True, max_age=60 * 24)
    return queue_entry
