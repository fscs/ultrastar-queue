from .parser import UltrastarFileParser


def print_songs(path: str = ""):
    from decouple import config

    if path == "":
        path = config("PATH_TO_ULTRASTAR_SONG_DIR")
    file_paths = UltrastarFileParser.get_song_file_paths(path)
    for file_path in file_paths:
        try:
            attr_dict = UltrastarFileParser.parse_file_for_ultrastar_song_attributes(file_path)
        except ValueError as e:
            print(f"Not an ultrastar file: {file_path}")
            print(e)
            continue

        print(attr_dict, "\n")


if __name__ == "__main__":
    print_songs()
