import os
from datetime import timedelta

from pydantic import BaseModel, Field, ConfigDict
from sqlmodel import SQLModel
from tinytag import TinyTag


class UltrastarSongBase(SQLModel):
    title: str
    artist: str
    audio_duration: timedelta | None = None
    lyrics: str | None = None

    model_config = ConfigDict(ser_json_timedelta='float')

    def __str__(self):
        repr_str = ""
        for attr in self.model_fields:
            if hasattr(self, attr):
                repr_str += f"{attr}: {getattr(self, attr)}\n"
        return "UltrastarSongBase(\n"+repr_str+")"


class UltrastarSongConverter(BaseModel):
    title: str
    artist: str
    audio_duration: timedelta | None = None
    lyrics: str | None = None
    audio: str = Field(default="", alias="mp3")

    model_config = ConfigDict(ser_json_timedelta='float')

    def __init__(self, **data):
        try:
            data["audio_duration"]
        except KeyError:
            pass
        else:
            if type(data["audio_duration"]) is float:
                data["audio_duration"] = timedelta(seconds=data["audio_duration"])
        finally:
            super().__init__(**data)

    def set_audio_duration(self, dir_path: str) -> None:
        audio_path = os.path.join(dir_path, self.audio)
        if not TinyTag.is_supported(audio_path):
            raise RuntimeError({"error": f"Unsupported file extension: {audio_path}",
                                "supported extensions": TinyTag.SUPPORTED_FILE_EXTENSIONS})
        audio = TinyTag.get(audio_path)
        self.audio_duration = timedelta(seconds=round(audio.duration))
