"""A Parser for parsing Ultrastar files.

Examples
--------
Get the paths of .txt files.

>>> path_list = UltrastarFileParser.get_song_file_paths(".")
["./ultrastarfile_1.txt", "./ultrastarfile_2.txt", "./notanultrastarfile.txt"]

Parse the files for Ultrastar attributes.

>>> for path in path_list:
>>>     attr_dict = UltrastarFileParser.parse_file_for_ultrastar_song_attributes(path)
        print(attr_dict)
{"title": "Best Title Ever", ..., "lyrics": "Best lyrics of all time"}
{"title": "2nd Best Title Ever", ..., "lyrics": "2nd Best lyrics of all time"}
Traceback (most recent call last):
    ...
UltrastarMatchingError: Line does not match any Ultrastar file format: This is not an Ultrastar file!

"""

import os
import re
import tokenize
from typing import Dict, List

from .exceptions import UltrastarMatchingError
from .schemas import UltrastarFileRegexMatcher


class UltrastarFileParser:
    """
    The class provides methods for parsing Ultrastar files.

    Methods
    ----------
    def get_song_file_paths(input_dir: str) -> List[str]
        Return all file paths starting from a given dir path that lead to a .txt file.

    def parse_file_for_ultrastar_song_attributes(cls, file_path: str) -> Dict[str, str]
        Return a dictionary with Attribute - Value pairs from an Ultrastar File.
    """

    @staticmethod
    def _get_lyrics_from_sing_line(line: str) -> str:
        """Return lyrics from line that was identified as a sing line.

        Return lyrics from a sing line cleaned from `~` and `\n`.
        """
        _, lyrics = re.split(pattern=UltrastarFileRegexMatcher.SING_LINE.value, string=line, maxsplit=1)
        lyrics = lyrics.replace("~", "")
        return lyrics.replace("\n", "")

    @staticmethod
    def _match_line_format(line: str) -> UltrastarFileRegexMatcher | None:
        """Return matching line format for an Ultrastarfile line."""
        for regex in UltrastarFileRegexMatcher:
            if re.search(regex.value, line):
                return UltrastarFileRegexMatcher(regex)
        return None

    @staticmethod
    def _get_attr_and_value_from_line(attribute_line: str) -> (str, str):
        """Return attribute and value from a line that was identified as an attribute line.

        Return attribute and value from a line that was identified as an attribute line.
        Attributes are saved as lowercase.
        """
        attr, value = attribute_line.split(":", 1)
        return attr.lstrip("#").lower(), value.replace("\n", "").strip()

    @staticmethod
    def _get_file_encoding(file_path: str) -> str:
        """Return encoding of a file at a given path."""
        with open(file_path, "rb") as file:
            try:
                encoding = tokenize.detect_encoding(file.readline)[0]
            except SyntaxError:
                encoding = "utf-8"
        return encoding

    @staticmethod
    def get_song_file_paths(input_dir: str) -> List[str]:
        """Return all file paths starting from a given dir path that lead to a .txt file.

        This function returns a list of all file paths that lead to a .txt file.
        It searches recursivly from the given starting dir for .txt files.

        Parameters
        ----------
        input_dir : str
            The path to the directory where the search for .txt files should start.

        Returns
        -------
        song_paths : list
            A list of str that are file paths leading to a .txt file.

        Raises
        ------
        FileNotFoundError
            If the given directory does not exist.
        """
        if not os.path.exists(input_dir):
            raise FileNotFoundError(f"Could not find path: {input_dir}")
        song_paths = [os.path.join(dir_path, file)
                      for dir_path, dir_names, files in os.walk(input_dir)
                      for file in files
                      if file.endswith(".txt")]
        return song_paths

    @classmethod
    def parse_file_for_ultrastar_song_attributes(cls, file_path: str, encoding: str = None) -> Dict[str, str]:
        """Return a dictionary with Attribute - Value pairs from an Ultrastar File.

        Parses the file at the given path for lines matching the Ultrastar file format.
        Lines matching the attribute format are saved with the attribute as key and the value as value.
        Lines matching the sing_line format are appended to the value at the key `lyrics`.
        Lines matching the player_delimiter format are currently ignored.

        Parameters
        ----------
        file_path : str
            The path to the file to be parsed.
        encoding: str, optional
            The encoding for the file.

        Returns
        -------
        ultrastar_song_attributes : dict
            A dictionary with Attribute - Value pairs from an Ultrastar file.

        Raises
        ------
        UltrastarMatchingError
            If a line in the file does not match the Ultrastar format.

        See Also
        -----
        ultrastar_file_parser.schemas.UltrastarFileRegexMatcher :
            The RegEx matching the Ultrastar line format.
        """
        ultrastar_song_attributes: Dict[str, str] = {}
        lyrics = ""
        if not encoding:
            encoding = cls._get_file_encoding(file_path)
        with open(file_path, "r", encoding=encoding) as file:
            for line in file:
                regex_match = cls._match_line_format(line)
                if regex_match is None:
                    raise UltrastarMatchingError(f"Line does not match any Ultrastar file format: {line}")
                if regex_match is UltrastarFileRegexMatcher.ATTRIBUTE:
                    attr, value = cls._get_attr_and_value_from_line(line)
                    ultrastar_song_attributes[attr] = value
                elif regex_match is UltrastarFileRegexMatcher.SING_LINE:
                    lyrics += cls._get_lyrics_from_sing_line(line)
                elif regex_match is UltrastarFileRegexMatcher.END_OF_PHRASE:
                    if lyrics and not lyrics.endswith(" "):
                        lyrics += " "
                elif regex_match is UltrastarFileRegexMatcher.PLAYER_DELIMITER:
                    pass

        ultrastar_song_attributes["lyrics"] = lyrics

        return ultrastar_song_attributes
