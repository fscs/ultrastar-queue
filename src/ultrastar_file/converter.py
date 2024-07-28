import os
from datetime import timedelta
from tinytag import TinyTag
from typing import Dict
from schemas import dict_cleaning_attributes


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


def _clean_attributes(attributes: Dict[str, str]) -> None:
    replaced_attributes = dict_cleaning_attributes["replaced_attributes"]
    old_attributes = attributes.copy()
    for attribute, value in old_attributes.items():
        if attribute in replaced_attributes.keys():
            value = attributes[attribute]
            new_attribute = replaced_attributes[attribute]
            attributes[new_attribute] = value
            del attributes[attribute]


def _get_audio_duration(path) -> float:
    if not TinyTag.is_supported(path):
        raise RuntimeError({"error": f"Unsupported file extension: {path}",
                            "supported extensions": TinyTag.SUPPORTED_FILE_EXTENSIONS})
    audio = TinyTag.get(path)
    return audio.duration


def update_ultrastar_song_attributes(dir_path: str, attributes: Dict[str, str]) -> None:
    _clean_attributes(attributes)
    audio_path = os.path.join(dir_path, attributes["audio"])
    print(audio_path)
    try:
        audio_duration_in_seconds = _get_audio_duration(audio_path)
    except RuntimeError as e:
        attributes["audio_duration_in_seconds"] = ""
        raise RuntimeError("Can not update attributes due to unsupported file extension") from e
    else:
        attributes["audio_duration_in_seconds"] = str(audio_duration_in_seconds)
