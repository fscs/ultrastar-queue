from sqlmodel import SQLModel, Field


class UltrastarSongBase(SQLModel):
    title: str
    artist: str
    lyrics: str | None = None


class UltrastarSong(UltrastarSongBase, table=True):
    id: int = Field(default=None, primary_key=True)


class UserBase(SQLModel):
    username: str
    is_admin: bool = False


class User(UserBase):
    hashed_password: str
