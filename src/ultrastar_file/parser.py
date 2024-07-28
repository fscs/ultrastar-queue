import re
import os
from decouple import config
from typing import Dict, List
from src.songs.schemas import UltrastarSongBase
from schemas import UltrastarFileRegexMatcher
from converter import UltrastarSongConverter, update_ultrastar_song_attributes


# https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
def get_song_file_paths(input_dir: str) -> List[str]:
    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"Could not find path: {input_dir}")
    song_paths = [os.path.join(dir_path, file)
                  for dir_path, dir_names, files in os.walk(input_dir)
                  for file in files
                  if file.endswith(".txt")]
    return song_paths


"""def _get_song_file(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        yield file.readline()"""


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
    # file = _get_song_file(file_path)
    # with open(file_path, "r", encoding="utf-8-sig") as file:
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            # print(line)
            # regex_match = _match_line_format(line.replace(r"\ufeff", ""))
            regex_match = _match_line_format(line)
            if regex_match is None:
                raise ValueError(f"Line does not match any Ultrastar file format: {line}")
            if regex_match is UltrastarFileRegexMatcher.ATTRIBUTE:
                attribute, value = _get_attr_and_value_from_line(line)
                ultrastar_song_attributes[attribute.lower()] = value
            elif regex_match is UltrastarFileRegexMatcher.SING_LINE:
                lyrics += _get_lyrics_from_sing_line(line)
                """ elif regex_match is UltrastarFileRegexMatcher.ATTRIBUTE_WITH_BOM_ENCODING:
                attribute, value = _get_attr_and_value_from_line(line.lstrip(r"uef"))
                ultrastar_song_attributes[attribute.lower()] = value"""
            else:
                pass

    ultrastar_song_attributes["lyrics"] = lyrics

    return ultrastar_song_attributes


def parse_ultrastar_files_to_ultrastar_song_base() -> UltrastarSongBase:
    path = config("PATH_TO_ULTRASTAR_SONG_DIR")
    files = get_song_file_paths(path)
    for file_path in files:
        try:
            attr_dict = parse_file_for_ultrastar_song_attributes(file_path)
        except ValueError as e:
            raise e
        update_ultrastar_song_attributes(os.path.dirname(file_path), attr_dict)
        song_converter = UltrastarSongConverter(**attr_dict)
        song_base: UltrastarSongBase = UltrastarSongBase(
            title=song_converter.title,
            artist=song_converter.artist,
            lyrics=song_converter.lyrics
        )
        print(song_base)
        return song_base
