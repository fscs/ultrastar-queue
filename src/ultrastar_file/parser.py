import re
import os
from typing import Dict, List
from .schemas import UltrastarFileRegexMatcher


def get_song_file_paths(input_dir: str) -> List[str]:
    if not os.path.exists(input_dir):
        raise FileNotFoundError("Could not find path: {path}".format(path=input_dir))
    song_paths = [os.path.join(dir_path, file)
                  for dir_path, dir_names, files in os.walk(input_dir)
                  for file in files
                  if file.endswith(".txt")]
    return song_paths


def _get_lyrics_from_sing_line(line: str) -> str:
    empty, lyrics = re.split(pattern=UltrastarFileRegexMatcher.SING_LINE.value, string=line, maxsplit=1)
    return lyrics.replace("\n", "")


def _match_line_format(line: str) -> UltrastarFileRegexMatcher | None:
    for regex in UltrastarFileRegexMatcher:
        if re.search(regex.value, line):
            return UltrastarFileRegexMatcher(regex)
    return None


def _get_attr_and_value_from_line(attribute_line: str) -> (str, str):
    attr, value = attribute_line.split(":", 1)
    attr = attr.lstrip("#")
    return attr.lstrip("#"), value.replace("\n", "")


def parse_file_for_ultrastar_song_attributes(file_path) -> Dict[str, str]:
    ultrastar_song_attributes: Dict[str, str] = {}
    lyrics = ""
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            regex_match = _match_line_format(line.lstrip("\ufeff"))
            if regex_match is None:
                raise ValueError(f"Line does not match any Ultrastar file format: {line}")
            if regex_match is UltrastarFileRegexMatcher.ATTRIBUTE:
                attribute, value = _get_attr_and_value_from_line(line)
                ultrastar_song_attributes[attribute.lower()] = value
            elif regex_match is UltrastarFileRegexMatcher.SING_LINE:
                lyrics += _get_lyrics_from_sing_line(line)
            else:
                pass

    ultrastar_song_attributes["lyrics"] = lyrics

    return ultrastar_song_attributes
