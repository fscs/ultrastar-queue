from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Cookie, Response, status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.app import db_controller
from src.auth.controller import is_admin
from src.database.controller import SessionController
from src.database.models import UltrastarSong
from .controller import QueueController
from .exceptions import (QueueClosedHTTPException,
                         QueueEmptyError,
                         QueueEmptyHTTPException,
                         QueueIndexError,
                         QueueIndexHTTPException,
                         SongAlreadySungHTTPException,
                         SongRecentlySungHTTPException,
                         CantSubmitSongHTTPException,
                         SongNotInDatabaseHTTPException,
                         SongAlreadyInQueueHTTPException,
                         MismatchingSongDataHTTPException,
                         NotAValidNumberHTTPException)
from .schemas import SongInQueue

queue_router = APIRouter(
    prefix="/queue",
    tags=["queue"],
    dependencies=[],
    responses={404: {"description": "Not found"}}
)

queue_controller = QueueController()
TIME_BETWEEN_SUBMITTING_SONGS: timedelta = timedelta(seconds=60)
SUBMITTING_SONGS_IN_TIMEFRAME_IS_BLOCKED: bool = True


@queue_router.get("/")
def get_queue():
    return queue_controller.queue


@queue_router.get("/processed-songs")
def get_processed_songs():
    return queue_controller.processed_songs


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

    song_in_db = await SessionController.get_song_by_id(session, requested_song_id)
    if not song_in_db:
        raise SongNotInDatabaseHTTPException()

    if queue_controller.is_song_in_queue(song_in_db):
        raise SongAlreadyInQueueHTTPException(detail=f"Song {song_in_db.title} by {song_in_db.artist} is "
                                                     f"already in queue")

    if not queue_controller.is_queue_open():
        raise QueueClosedHTTPException()

    if queue_controller.has_song_been_sung_max_times(song_in_db):
        raise SongAlreadySungHTTPException(detail=f"Song {song_in_db.title} by {song_in_db.artist} has "
                                                  f"already been sung a few times today. Please choose another one.")

    if not queue_controller.will_time_between_songs_have_passed_until_end_of_queue(song_in_db):
        raise SongRecentlySungHTTPException(detail=f"Song {song_in_db.title} by {song_in_db.artist} has "
                                                   "been sung recently. Please choose another one.")

    song_in_queue = SongInQueue(song=song_in_db, singer=singer)

    queue_controller.add_song_at_end(song_in_queue)

    response.set_cookie("last_added", str(datetime.now()), httponly=True, max_age=60*24)
    return song_in_queue


@queue_router.post("/add-song-as-admin",
                   status_code=status.HTTP_201_CREATED,
                   response_model=SongInQueue,
                   dependencies=[Depends(is_admin)])
async def add_song_to_queue_as_admin(
        requested_song_id: int,
        singer: str,
        session: AsyncSession = Depends(db_controller.get_session)
):
    song_in_db = await SessionController.get_song_by_id(session, requested_song_id)
    if not song_in_db:
        raise SongNotInDatabaseHTTPException()

    song_in_queue = SongInQueue(song=song_in_db, singer=singer)
    queue_controller.add_song_at_end(song_in_queue)

    return song_in_queue


@queue_router.put("/check-first-song", dependencies=[Depends(is_admin)])
def check_first_song_in_queue():
    try:
        checked = queue_controller.mark_first_song_as_processed()
    except QueueEmptyError as err:
        raise QueueEmptyHTTPException(detail=err.msg)
    return {"checked": checked}


@queue_router.delete("/remove-song", dependencies=[Depends(is_admin)])
def remove_song_from_queue(index: int):
    try:
        removed = queue_controller.remove_song_by_index(index)
    except QueueIndexError as err:
        raise QueueIndexHTTPException(detail=err.msg)
    return {"deleted": removed}


@queue_router.delete("/clear-queue", dependencies=[Depends(is_admin)])
def clear_queue():
    queue_controller.clear_queue()
    return {"message": "Queue cleared"}


@queue_router.delete("/clear-processed-songs", dependencies=[Depends(is_admin)])
def clear_processed_songs():
    queue_controller.clear_processed_songs()
    return {"message": "Processed songs cleared"}


@queue_router.delete("/clear-queue-controller", dependencies=[Depends(is_admin)])
def clear_queue_controller():
    queue_controller.clear_queue_controller()
    return {"message": "Queue controller cleared"}


@queue_router.get("/get-time-between-same-song", dependencies=[Depends(is_admin)])
def get_time_between_same_song() -> int:
    return round(queue_controller.time_between_same_song.total_seconds())


@queue_router.put("/set-time-between-same-song", dependencies=[Depends(is_admin)])
def set_time_between_same_song(hours: int, minutes: int, seconds: int):
    try:
        queue_controller.time_between_same_song = timedelta(hours=hours, minutes=minutes, seconds=seconds)
    except ValueError as err:
        raise NotAValidNumberHTTPException(detail=err.args[0])
    return {"message": f"Set time to {timedelta(hours=hours, minutes=minutes, seconds=seconds)} "
                       f"between submitting the same song"}


@queue_router.get("/get-max-times-song-can-be-sung", dependencies=[Depends(is_admin)])
def get_max_times_song_can_be_sung() -> int:
    return queue_controller.max_times_song_can_be_sung


@queue_router.put("/set-max-times-song-can-be-sung", dependencies=[Depends(is_admin)])
def set_max_times_song_can_be_sung(max_times: int):
    try:
        queue_controller.max_times_song_can_be_sung = max_times
    except ValueError as err:
        raise NotAValidNumberHTTPException(detail=err.args[0])
    return {"message": f"Set max times the same song can be sung to {max_times}"}


@queue_router.get("/get-time-between-submitting-songs", dependencies=[Depends(is_admin)])
def get_time_between_submitting_songs() -> int:
    return round(TIME_BETWEEN_SUBMITTING_SONGS.total_seconds())


@queue_router.put("/set-time-between-submitting-songs", dependencies=[Depends(is_admin)])
def set_time_between_submitting_songs(seconds: int, minutes: int, hours: int):
    time_between_submitting_songs = timedelta(seconds=seconds, minutes=minutes, hours=hours)
    if time_between_submitting_songs.total_seconds() < 0:
        raise NotAValidNumberHTTPException(detail="Time cannot be negative")
    global TIME_BETWEEN_SUBMITTING_SONGS
    TIME_BETWEEN_SUBMITTING_SONGS = time_between_submitting_songs
    return {"message": f"Set time between submitting songs to {TIME_BETWEEN_SUBMITTING_SONGS}"}


@queue_router.get("/get-block-submitting-songs-in-timeframe", dependencies=[Depends(is_admin)])
def get_blocks_submitting_songs_in_timeframe() -> bool:
    return SUBMITTING_SONGS_IN_TIMEFRAME_IS_BLOCKED


@queue_router.put("/set-block-submitting-songs-in-timeframe", dependencies=[Depends(is_admin)])
def set_block_submitting_songs_in_timeframe(block_submitting: bool):
    global SUBMITTING_SONGS_IN_TIMEFRAME_IS_BLOCKED
    SUBMITTING_SONGS_IN_TIMEFRAME_IS_BLOCKED = block_submitting
    return {"message": f"Set block submitting songs in timeframe to {SUBMITTING_SONGS_IN_TIMEFRAME_IS_BLOCKED}"}


@queue_router.put("/check-song-by-index", dependencies=[Depends(is_admin)])
def check_song_in_queue_by_index(index: int):
    try:
        checked = queue_controller.mark_song_at_index_as_processed(index)
    except QueueEmptyError as err:
        raise QueueEmptyHTTPException(detail=err.msg)
    return {"message": f"checked: {checked.song.title} by {checked.song.artist}"}


@queue_router.get("/get-is-queue-open", dependencies=[Depends(is_admin)])
def get_is_queue_open() -> bool:
    return queue_controller.is_queue_open()


@queue_router.put("/set-is-queue-open", dependencies=[Depends(is_admin)])
def set_is_queue_open(open_queue: bool):
    if open_queue:
        queue_controller.open_queue()
    else:
        queue_controller.close_queue()
    return {"message": f"Set is queue open to {queue_controller.is_queue_open()}"}
