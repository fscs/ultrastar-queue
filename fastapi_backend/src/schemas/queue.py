from datetime import datetime

from pydantic import BaseModel

from ..models.songs import UltrastarSong


class SongInQueue(BaseModel):
    song: UltrastarSong
    singer: str


class ProcessedSong(BaseModel):
    song: UltrastarSong
    processed_at: datetime
