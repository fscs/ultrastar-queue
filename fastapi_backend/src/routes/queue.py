from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Cookie, Response, status
from sqlmodel.ext.asyncio.session import AsyncSession

from ..app import queue_service, db_controller
from ..exceptions.queue import (QueueClosedHTTPException,
                                SongAlreadySungHTTPException,
                                SongRecentlySungHTTPException,
                                CantSubmitSongHTTPException,
                                SongNotInDatabaseHTTPException,
                                SongAlreadyInQueueHTTPException)
from ..schemas.queue import SongInQueue
from ..services.session import SessionService

queue_router = APIRouter(
    prefix="/queue",
    tags=["queue"],
    dependencies=[],
    responses={404: {"description": "Not found"}}
)

TIME_BETWEEN_SUBMITTING_SONGS: timedelta = timedelta(seconds=60)  # TODO
SUBMITTING_SONGS_IN_TIMEFRAME_IS_BLOCKED: bool = True  # TODO


@queue_router.get("/")
def get_queue():
    return queue_service.queue


@queue_router.get("/processed-songs")
def get_processed_songs():
    return queue_service.processed_songs


@queue_router.post("/add-song", status_code=status.HTTP_201_CREATED, response_model=SongInQueue)
async def add_song_to_queue(
        response: Response,
        requested_song_id: int,
        singer: str,
        session: AsyncSession = Depends(db_controller.get_session),
        last_added: datetime | None = Cookie(None)
):
    if last_added is not None:
        if last_added > (datetime.now() - TIME_BETWEEN_SUBMITTING_SONGS):
            raise CantSubmitSongHTTPException(
                detail=f"Please wait {TIME_BETWEEN_SUBMITTING_SONGS} before submitting a new song"
            )

    song_in_db = await SessionService.get_song_by_id(session, requested_song_id)
    if not song_in_db:
        raise SongNotInDatabaseHTTPException()

    if queue_service.is_song_in_queue(song_in_db):
        raise SongAlreadyInQueueHTTPException(detail=f"Song {song_in_db.title} by {song_in_db.artist} is "
                                                     f"already in queue")

    if not queue_service.is_queue_open():
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
