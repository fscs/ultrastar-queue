import os
import re
import tokenize
from typing import Dict, List

from .schemas import UltrastarFileRegexMatcher


class UltrastarFileParser:

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
        return attr.lstrip("#").lower(), value.replace("\n", "").strip()

    @staticmethod
    def _get_file_encoding(file_path: str) -> str:
        with open(file_path, "rb") as file:
            try:
                encoding = tokenize.detect_encoding(file.readline)[0]
            except SyntaxError:
                encoding = "utf-8"
        return encoding

    @staticmethod
    def get_song_file_paths(input_dir: str) -> List[str]:
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
                    attr, value = cls._get_attr_and_value_from_line(line)
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
