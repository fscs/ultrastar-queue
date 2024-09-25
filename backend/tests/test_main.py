from fastapi import status, HTTPException

from src.app.main import queue_service
from src.app.queue.config import QueueBaseSettings


def overrides_is_admin_as_false():
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not enough privileges")


def clean_queue_test_setup(client):
    client.cookies.clear()
    queue_service.clear_queue_service()
    queue_service.time_between_same_song = QueueBaseSettings.TIME_BETWEEN_SAME_SONG
    queue_service.max_times_song_can_be_sung = QueueBaseSettings.MAX_TIMES_SONG_CAN_BE_SUNG
    queue_service.time_between_song_submissions = QueueBaseSettings.TIME_BETWEEN_SONG_SUBMISSIONS
