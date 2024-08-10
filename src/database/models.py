from sqlmodel import Field, SQLModel

from src.songs.schemas import UltrastarSongBase


class UltrastarSong(UltrastarSongBase, table=True):
    id: int = Field(default=None, primary_key=True)


class User(SQLModel, table=True):
    username: str = Field(primary_key=True)
    is_admin: bool = False
    hashed_password: str
