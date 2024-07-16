from pydantic import BaseModel
from src.database.models import UltrastarSong


class SongInQueue(BaseModel):
    song: UltrastarSong
    singer: str
