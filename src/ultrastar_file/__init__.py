from decouple import config
from converter import update_ultrastar_song_attributes
from schemas import UltrastarSongConverter
from src.songs.schemas import UltrastarSongBase
import parser
import os

if __name__ == "__main__":
    path = config("PATH_TO_ULTRASTAR_SONG_DIR")
    files = parser.get_song_file_paths(path)
    attr_dict = {}
    for file_path in files:
        try:
            attr_dict = parser.parse_file_for_ultrastar_song_attributes(file_path)
        except ValueError as e:
            print(f"Not an ultrastar file: {file_path}")
            continue
        update_ultrastar_song_attributes(os.path.dirname(file_path), attr_dict)
        song_converter = UltrastarSongConverter(**attr_dict)
        song_base: UltrastarSongBase = UltrastarSongBase(
            title=song_converter.title,
            artist=song_converter.artist,
            lyrics=song_converter.lyrics
        )
        print(song_base)
