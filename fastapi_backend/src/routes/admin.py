from datetime import timedelta

from fastapi import Depends, APIRouter, status
from sqlmodel.ext.asyncio.session import AsyncSession

from fastapi_backend.src.models.songs import UltrastarSong
from ..app import db_controller, queue_service
from ..exceptions.queue import (SongNotInDatabaseHTTPException, QueueEmptyError, NotAValidNumberHTTPException,
                                QueueEmptyHTTPException, QueueIndexError, QueueIndexHTTPException)
from ..schemas.queue import SongInQueue
from ..schemas.songs import UltrastarSongBase
from ..services import auth
from ..services.session import SessionService

admin_router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.is_admin)],
    responses={404: {"description": "Not found"}}
)


@admin_router.post("/add-song-as-admin",
                   status_code=status.HTTP_201_CREATED,
                   response_model=SongInQueue,
                   dependencies=[Depends(auth.is_admin)])
async def add_song_to_queue_as_admin(
        requested_song_id: int,
        singer: str,
        session: AsyncSession = Depends(db_controller.get_session)
):
    song_in_db = await SessionService.get_song_by_id(session, requested_song_id)
    if not song_in_db:
        raise SongNotInDatabaseHTTPException()

    song_in_queue = SongInQueue(song=song_in_db, singer=singer)
    queue_service.add_song_at_end(song_in_queue)

    return song_in_queue


@admin_router.put("/check-first-song", dependencies=[Depends(auth.is_admin)])
def check_first_song_in_queue():
    try:
        checked = queue_service.mark_first_song_as_processed()
    except QueueEmptyError as err:
        raise QueueEmptyHTTPException(detail=err.msg)
    return {"checked": checked}


@admin_router.delete("/remove-song", dependencies=[Depends(auth.is_admin)])
def remove_song_from_queue(index: int):
    try:
        removed = queue_service.remove_song_by_index(index)
    except QueueIndexError as err:
        raise QueueIndexHTTPException(detail=err.msg)
    return {"deleted": removed}


@admin_router.delete("/clear-queue", dependencies=[Depends(auth.is_admin)])
def clear_queue():
    queue_service.clear_queue()
    return {"message": "Queue cleared"}


@admin_router.delete("/clear-processed-songs", dependencies=[Depends(auth.is_admin)])
def clear_processed_songs():
    queue_service.clear_processed_songs()
    return {"message": "Processed songs cleared"}


@admin_router.delete("/clear-queue-service", dependencies=[Depends(auth.is_admin)])
def clear_queue_service():
    queue_service.clear_queue_service()
    return {"message": "Queue Service cleared"}


@admin_router.get("/get-time-between-same-song", dependencies=[Depends(auth.is_admin)])
def get_time_between_same_song() -> int:
    return round(queue_service.time_between_same_song.total_seconds())


@admin_router.put("/set-time-between-same-song", dependencies=[Depends(auth.is_admin)])
def set_time_between_same_song(hours: int, minutes: int, seconds: int):
    try:
        queue_service.time_between_same_song = timedelta(hours=hours, minutes=minutes, seconds=seconds)
    except ValueError as err:
        raise NotAValidNumberHTTPException(detail=err.args[0])
    return {"message": f"Set time to {timedelta(hours=hours, minutes=minutes, seconds=seconds)} "
                       f"between submitting the same song"}


@admin_router.get("/get-max-times-song-can-be-sung", dependencies=[Depends(auth.is_admin)])
def get_max_times_song_can_be_sung() -> int:
    return queue_service.max_times_song_can_be_sung


@admin_router.put("/set-max-times-song-can-be-sung", dependencies=[Depends(auth.is_admin)])
def set_max_times_song_can_be_sung(max_times: int):
    try:
        queue_service.max_times_song_can_be_sung = max_times
    except ValueError as err:
        raise NotAValidNumberHTTPException(detail=err.args[0])
    return {"message": f"Set max times the same song can be sung to {max_times}"}


@admin_router.get("/get-time-between-submitting-songs", dependencies=[Depends(auth.is_admin)])
def get_time_between_submitting_songs() -> int:
    return round(TIME_BETWEEN_SUBMITTING_SONGS.total_seconds())


@admin_router.put("/set-time-between-submitting-songs", dependencies=[Depends(auth.is_admin)])
def set_time_between_submitting_songs(seconds: int, minutes: int, hours: int):
    time_between_submitting_songs = timedelta(seconds=seconds, minutes=minutes, hours=hours)
    if time_between_submitting_songs.total_seconds() < 0:
        raise NotAValidNumberHTTPException(detail="Time cannot be negative")
    global TIME_BETWEEN_SUBMITTING_SONGS
    TIME_BETWEEN_SUBMITTING_SONGS = time_between_submitting_songs
    return {"message": f"Set time between submitting songs to {TIME_BETWEEN_SUBMITTING_SONGS}"}


@admin_router.get("/get-block-submitting-songs-in-timeframe", dependencies=[Depends(auth.is_admin)])
def get_blocks_submitting_songs_in_timeframe() -> bool:
    return SUBMITTING_SONGS_IN_TIMEFRAME_IS_BLOCKED


@admin_router.put("/set-block-submitting-songs-in-timeframe", dependencies=[Depends(auth.is_admin)])
def set_block_submitting_songs_in_timeframe(block_submitting: bool):
    global SUBMITTING_SONGS_IN_TIMEFRAME_IS_BLOCKED
    SUBMITTING_SONGS_IN_TIMEFRAME_IS_BLOCKED = block_submitting
    return {"message": f"Set block submitting songs in timeframe to {SUBMITTING_SONGS_IN_TIMEFRAME_IS_BLOCKED}"}


@admin_router.put("/check-song-by-index", dependencies=[Depends(auth.is_admin)])
def check_song_in_queue_by_index(index: int):
    try:
        checked = queue_service.mark_song_at_index_as_processed(index)
    except QueueEmptyError as err:
        raise QueueEmptyHTTPException(detail=err.msg)
    return {"message": f"checked: {checked.song.title} by {checked.song.artist}"}


@admin_router.get("/get-is-queue-open", dependencies=[Depends(auth.is_admin)])
def get_is_queue_open() -> bool:
    return queue_service.is_queue_open()


@admin_router.put("/set-is-queue-open", dependencies=[Depends(auth.is_admin)])
def set_is_queue_open(open_queue: bool):
    if open_queue:
        queue_service.open_queue()
    else:
        queue_service.close_queue()
    return {"message": f"Set is queue open to {queue_service.is_queue_open()}"}


@admin_router.post("/create-song", dependencies=[Depends(auth.is_admin)], status_code=status.HTTP_201_CREATED)
async def create_song(
        song_data: UltrastarSongBase,
        session: AsyncSession = Depends(db_controller.get_session)
) -> UltrastarSong:
    song = UltrastarSong(**song_data.model_dump())
    song = await SessionService.add_song(session=session, song=song)
    return song
