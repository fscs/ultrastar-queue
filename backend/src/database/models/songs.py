from sqlmodel import Field

from backend.src.app.schemas.songs import UltrastarSongBase


class UltrastarSong(UltrastarSongBase, table=True):
    id: int = Field(default=None, primary_key=True)
