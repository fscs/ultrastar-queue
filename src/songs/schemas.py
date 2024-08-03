from sqlmodel import SQLModel
from datetime import timedelta


class UltrastarSongBase(SQLModel):
    title: str
    artist: str
    lyrics: str | None = None

    def __str__(self):
        repr_str = ""
        for attr in self.model_fields:
            if hasattr(self, attr):
                repr_str += f"{attr}: {getattr(self, attr)}\n"
        return "UltrastarSongBase(\n"+repr_str+")"


class UltrastarSongConverter:
    def __init__(self, title: str, artist: str, lyrics: str, audio_duration_in_seconds: str, *args, **kwargs) -> None:
        self.title: str = title
        self.artist: str = artist
        self.lyrics: str | None = lyrics if len(lyrics) > 0 else None
        self.audio_duration: timedelta | None = (  # TODO irgendwas stimmt hier nicht
            timedelta(float(audio_duration_in_seconds))
            if len(audio_duration_in_seconds) > 0
            else None
        )
