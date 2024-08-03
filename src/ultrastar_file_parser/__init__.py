from src.ultrastar_file_parser.parser import UltrastarFileParser

if __name__ == "__main__":
    import os
    from decouple import config
    from src.songs.schemas import UltrastarSongBase, UltrastarSongConverter

    path = config("PATH_TO_ULTRASTAR_SONG_DIR")
    files = UltrastarFileParser.get_song_file_paths(path)
    for file_path in files:
        try:
            attr_dict = UltrastarFileParser.parse_file_for_ultrastar_song_attributes(file_path)
        except ValueError as e:
            print(f"Not an ultrastar file: {file_path}")
            print(e)
            continue
        audio_duration = UltrastarFileParser.get_audio_duration(os.path.dirname(file_path), attr_dict["audio"])
        attr_dict["audio_duration_in_seconds"] = audio_duration
        song_converter = UltrastarSongConverter(**attr_dict)
        song_base: UltrastarSongBase = UltrastarSongBase(
            title=song_converter.title,
            artist=song_converter.artist,
            lyrics=song_converter.lyrics
        )

        print(song_base, "\n")
