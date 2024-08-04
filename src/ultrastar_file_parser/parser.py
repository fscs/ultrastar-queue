import os
import re
import tokenize
from typing import Dict, List

from tinytag import TinyTag

from .schemas import UltrastarFileRegexMatcher


class UltrastarFileParser:
    # from https://usdx.eu/format/#specs accessesed at 27.07.2024
    replaced_ultrastar_song_attributes = {
        "MP3": "audio",
        "DUETSINGERP1": "p1",
        "DUETSINGERP2": "p2",
        "AUTHOR": "creator",
        "PREVIEW": "previewstart"
    }

    @staticmethod
    def _get_lyrics_from_sing_line(line: str) -> str:
        empty, lyrics = re.split(pattern=UltrastarFileRegexMatcher.SING_LINE.value, string=line, maxsplit=1)
        lyrics = lyrics.replace("~", "")
        return lyrics.replace("\n", "")

    @staticmethod
    def _match_line_format(line: str) -> UltrastarFileRegexMatcher | None:
        for regex in UltrastarFileRegexMatcher:
            if re.search(regex.value, line):
                return UltrastarFileRegexMatcher(regex)
        return None

    @staticmethod
    def _get_attr_and_value_from_line(attribute_line: str) -> (str, str):
        attr, value = attribute_line.split(":", 1)
        return attr.lstrip("#"), value.replace("\n", "").strip()

    @staticmethod
    def _get_file_encoding(file_path: str) -> str:
        with open(file_path, "rb") as file:
            try:
                encoding = tokenize.detect_encoding(file.readline)[0]
            except SyntaxError:
                encoding = "utf-8"
        return encoding

    @staticmethod
    def _get_audio_duration_from_file(path: str) -> float:
        if not TinyTag.is_supported(path):
            raise RuntimeError({"error": f"Unsupported file extension: {path}",
                                "supported extensions": TinyTag.SUPPORTED_FILE_EXTENSIONS})
        audio = TinyTag.get(path)
        return audio.duration

    @classmethod
    def _get_cleaned_attr_and_value_from_line(cls, line: str) -> (str, str):
        attribute, value = cls._get_attr_and_value_from_line(line)
        if attribute in cls.replaced_ultrastar_song_attributes:
            return cls.replaced_ultrastar_song_attributes[attribute], value
        else:
            return attribute.lower(), value

    @classmethod
    def get_audio_duration(cls, dir_path: str, audio_file_name: str) -> str:
        audio_path = os.path.join(dir_path, audio_file_name)
        try:
            audio_duration_in_seconds = cls._get_audio_duration_from_file(audio_path)
        except RuntimeError as e:
            raise RuntimeError("Can not get audio duration due to unsupported file extension") from e
            # return ""
        else:
            return str(audio_duration_in_seconds)

    @classmethod
    def get_song_file_paths(cls, input_dir: str) -> List[str]:
        if not os.path.exists(input_dir):
            raise FileNotFoundError("Could not find path: {path}".format(path=input_dir))
        song_paths = [os.path.join(dir_path, file)
                      for dir_path, dir_names, files in os.walk(input_dir)
                      for file in files
                      if file.endswith(".txt")]
        return song_paths

    @classmethod
    def parse_file_for_ultrastar_song_attributes(cls, file_path: str) -> Dict[str, str]:
        ultrastar_song_attributes: Dict[str, str] = {}
        lyrics = ""
        encoding = cls._get_file_encoding(file_path)
        with open(file_path, "r", encoding=encoding) as file:
            for line in file:
                regex_match = cls._match_line_format(line)
                if regex_match is None:
                    raise ValueError(f"Line does not match any Ultrastar file format: {line}")
                if regex_match is UltrastarFileRegexMatcher.ATTRIBUTE:
                    attr, value = cls._get_cleaned_attr_and_value_from_line(line)
                    ultrastar_song_attributes[attr] = value
                elif regex_match is UltrastarFileRegexMatcher.SING_LINE:
                    lyrics += cls._get_lyrics_from_sing_line(line)
                elif regex_match is UltrastarFileRegexMatcher.END_OF_PHRASE:
                    if lyrics and not lyrics.endswith(" "):
                        lyrics += " "
                else:
                    pass

        ultrastar_song_attributes["lyrics"] = lyrics

        return ultrastar_song_attributes
