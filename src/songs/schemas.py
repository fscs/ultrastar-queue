from sqlmodel import SQLModel


class UltrastarSongBase(SQLModel):
    title: str
    artist: str
    lyrics: str | None = None
