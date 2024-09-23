from datetime import timedelta

from fastapi import APIRouter, status, Depends
from src.app.queue.exceptions import (QueueEmptyError,
                                      QueueIndexError,
                                      QueueIndexHTTPException,
                                      QueueEmptyHTTPException,
                                      SongNotInDatabaseHTTPException,
                                      NotAValidNumberHTTPException)
from src.app.queue.schemas import QueueEntry
from src.app.songs import crud as crud_songs

from ..dependencies import is_admin, AsyncSessionDep
from ..main import queue_service

admin_router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(is_admin)],
    responses={404: {"description": "Not found"}}
)


@admin_router.post("/add-entry-as-admin", status_code=status.HTTP_201_CREATED, response_model=QueueEntry)
async def add_entry_to_queue_as_admin(session: AsyncSessionDep, requested_song_id: int, singer: str):
    song = await crud_songs.get_song_by_id(session, requested_song_id)
    if not song:
        raise SongNotInDatabaseHTTPException()

    entry = QueueEntry(song=song, singer=singer)
    queue_service.add_entry_at_end(entry)

    return entry


@admin_router.put("/mark-first-entry-as-processed")
def mark_first_entry_in_queue_as_processed():
    try:
        marked = queue_service.mark_first_entry_as_processed()
    except QueueEmptyError as err:
        raise QueueEmptyHTTPException(detail=err.msg)
    return {"Marked as processed": marked}


@admin_router.put("/mark-entry-at-index-as-processed")
def mark_entry_in_queue_at_index_as_processed(index: int):
    try:
        marked = queue_service.mark_entry_at_index_as_processed(index)
    except QueueEmptyError as err:
        raise QueueEmptyHTTPException(detail=err.msg)
    return {"message": f"Marked as processed: {marked.song.title} by {marked.song.artist}"}


@admin_router.delete("/remove-entry")
def remove_entry_from_queue(index: int):
    try:
        removed = queue_service.remove_entry_by_index(index)
    except QueueIndexError as err:
        raise QueueIndexHTTPException(detail=err.msg)
    return {"deleted": removed}


@admin_router.delete("/clear-queue")
def clear_queue():
    queue_service.clear_queue()
    return {"message": "Queue cleared"}


@admin_router.delete("/clear-processed-entries")
def clear_processed_entries():
    queue_service.clear_processed_entries()
    return {"message": "Processed entries cleared"}


@admin_router.delete("/clear-queue-service")
def clear_queue_service():
    queue_service.clear_queue_service()
    return {"message": "Queue Service cleared"}


@admin_router.get("/get-time-between-same-song")
def get_time_between_same_song() -> int:
    return round(queue_service.time_between_same_song.total_seconds())


@admin_router.put("/set-time-between-same-song")
def set_time_between_same_song(hours: int, minutes: int, seconds: int):
    try:
        queue_service.time_between_same_song = timedelta(hours=hours, minutes=minutes, seconds=seconds)
    except ValueError as err:
        raise NotAValidNumberHTTPException(detail=err.args[0])
    return {"message": f"Set time to {timedelta(hours=hours, minutes=minutes, seconds=seconds)} "
                       f"between submitting the same song"}


@admin_router.get("/get-max-times-song-can-be-sung")
def get_max_times_song_can_be_sung() -> int:
    return queue_service.max_times_song_can_be_sung


@admin_router.put("/set-max-times-song-can-be-sung")
def set_max_times_song_can_be_sung(max_times: int):
    try:
        queue_service.max_times_song_can_be_sung = max_times
    except ValueError as err:
        raise NotAValidNumberHTTPException(detail=err.args[0])
    return {"message": f"Set max times the same song can be sung to {max_times}"}


@admin_router.get("/get-time-between-song-submissions")
def get_time_between_song_submissions() -> int:
    return round(queue_service.time_between_song_submissions.total_seconds())


@admin_router.put("/set-time-between-song-submissions")
def set_time_between_song_submissions(seconds: int, minutes: int, hours: int):
    time_between_song_submissions = timedelta(seconds=seconds, minutes=minutes, hours=hours)
    if time_between_song_submissions.total_seconds() < 0:
        raise NotAValidNumberHTTPException(detail="Time cannot be negative")
    queue_service.time_between_song_submissions = time_between_song_submissions
    return {"message": f"Set time between song submissions to {queue_service.time_between_song_submissions}"}


@admin_router.get("/get-queue-is-open")
def get_queue_is_open() -> bool:
    return queue_service.queue_is_open


@admin_router.put("/set-queue-is-open")
def set_queue_is_open(open_queue: bool):
    queue_service.queue_is_open = open_queue
    return {"message": f"Set queue is open to {queue_service.queue_is_open}"}
