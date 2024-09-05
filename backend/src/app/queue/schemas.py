from datetime import datetime

from pydantic import BaseModel

from ..songs.models import UltrastarSong


class SongInQueue(BaseModel):
    song: UltrastarSong
    singer: str


class ProcessedSong(BaseModel):
    song: UltrastarSong
    processed_at: datetime
