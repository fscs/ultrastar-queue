from datetime import datetime

from fastapi import APIRouter, Cookie, Response, status

from .exceptions import (QueueClosedHTTPException,
                         SongAlreadySungHTTPException,
                         SongRecentlySungHTTPException,
                         CantSubmitSongHTTPException,
                         SongNotInDatabaseHTTPException,
                         SongAlreadyInQueueHTTPException)
from .schemas import SongInQueue
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


@queue_router.get("/processed-songs")
def get_processed_songs():
    return queue_service.processed_songs


@queue_router.post("/add-song", status_code=status.HTTP_201_CREATED, response_model=SongInQueue)
async def add_song_to_queue(
        session: AsyncSessionDep,
        response: Response,
        requested_song_id: int,
        singer: str,
        last_added: datetime | None = Cookie(None)
):
    if last_added is not None:
        if last_added > (datetime.now() - queue_service.time_between_song_submissions):
            raise CantSubmitSongHTTPException(
                detail=f"Please wait {queue_service.time_between_song_submissions} before submitting a new song"
            )

    song_in_db = await get_song_by_id(session, requested_song_id)
    if not song_in_db:
        raise SongNotInDatabaseHTTPException()

    if queue_service.is_song_in_queue(song_in_db):
        raise SongAlreadyInQueueHTTPException(detail=f"Song {song_in_db.title} by {song_in_db.artist} is "
                                                     f"already in queue")

    if not queue_service.queue_is_open:
        raise QueueClosedHTTPException()

    if queue_service.has_song_been_sung_max_times(song_in_db):
        raise SongAlreadySungHTTPException(detail=f"Song {song_in_db.title} by {song_in_db.artist} has "
                                                  f"already been sung a few times today. Please choose another one.")

    if not queue_service.will_time_between_songs_have_passed_until_end_of_queue(song_in_db):
        raise SongRecentlySungHTTPException(detail=f"Song {song_in_db.title} by {song_in_db.artist} has "
                                                   "been sung recently. Please choose another one.")

    song_in_queue = SongInQueue(song=song_in_db, singer=singer)

    queue_service.add_song_at_end(song_in_queue)

    response.set_cookie("last_added", str(datetime.now()), httponly=True, max_age=60 * 24)
    return song_in_queue
