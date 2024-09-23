from datetime import datetime

from pydantic import BaseModel

from ..songs.models import UltrastarSong


class QueueEntry(BaseModel):
    song: UltrastarSong
    singer: str


class ProcessedQueueEntry(QueueEntry):
    processed_at: datetime
