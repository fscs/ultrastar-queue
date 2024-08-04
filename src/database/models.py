from sqlmodel import Field

from src.auth.schemas import UserBase
from src.songs.schemas import UltrastarSongBase


class UltrastarSong(UltrastarSongBase, table=True):
    id: int = Field(default=None, primary_key=True)


class User(UserBase):
    hashed_password: str
