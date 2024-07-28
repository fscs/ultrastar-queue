from enum import Flag, StrEnum, Enum


# from https://usdx.eu/format/#specs accessesed at 27.07.2024
class UltrastarFileAttributes(StrEnum):
    TITLE = "#TITLE"                    # mandatory
    ARTIST = "#ARTIST"                  # mandatory
    BPM = "#BPM"                        # mandatory
    MP3 = "#MP3"                        # formerly mandatory, now == AUDIO
    VERSION = "#VERSION"                # mandatory (new)
    AUDIO = "#AUDIO"                    # mandatory (new)
    GAP = "#GAP"
    COVER = "#COVER"
    BACKGROUND = "#BACKGROUND"
    VIDEO = "#VIDEO"
    VIDEOGAP = "#VIDEOGAP"
    GENRE = "#GENRE"
    EDITION = "#EDITION"
    CREATOR = "#CREATOR"
    LANGUAGE = "#LANGUAGE"
    YEAR = "#YEAR"
    START = "#START"
    END = "#END"
    PREVIEWSTART = "#PREVIEWSTART"
    MEDLEYSTARTBEAT = "#MEDLEYSTARTBEAT"
    MEDLEYENDBEAT = "#MEDLEYENDBEAT"
    CALCMEDLEY = "#CALCMEDLEY"
    P1 = "#P1"
    P2 = "#P2"
    P3 = "#P3"
    P4 = "#P4"
    COMMENT = "#COMMENT"
    VOCALS = "#VOCALS"                  # new
    INSTRUMENTAL = "#INSTRUMENTAL"      # new
    TAGS = "#TAGS"                      # new
    PROVIDEDBY = "#PROVIDEDBY"          # new
    RELATIVE = "#RELATIVE"              # deprecated
    DUETSINGERP1 = "#DUETSINGERP1"      # deprecated == P1
    DUETSINGERP2 = "#DUETSINGERP2"      # deprecated == P2
    RESOLUTION = "#RESOLUTION"          # deprecated
    NOTESGAP = "#NOTESGAP"              # deprecated
    ENCODING = "#ENCODING"              # deprecated
    AUTHOR = "#AUTHOR"                  # deprecated == CREATOR
    PREVIEW = "#PREVIEW"                # deprecated == PREVIEWSTART
    ALBUM = "#ALBUM"                    # deprecated
    SOURCE = "#SOURCE"                  # deprecated
    YOUTUBE = "#YOUTUBE"                # deprecated
    LENGTH = "#LENGTH"                  # deprecated
    FIXER = "#FIXER"                    # deprecated


dict_cleaning_attributes = {
    "deprecated_attributes": [
        UltrastarFileAttributes.RELATIVE.name.lower(),
        UltrastarFileAttributes.RESOLUTION.name.lower(),
        UltrastarFileAttributes.NOTESGAP.name.lower(),
        UltrastarFileAttributes.ENCODING.name.lower(),
        UltrastarFileAttributes.ALBUM.name.lower(),
        UltrastarFileAttributes.SOURCE.name.lower(),
        UltrastarFileAttributes.YOUTUBE.name.lower(),
        UltrastarFileAttributes.LENGTH.name.lower(),
        UltrastarFileAttributes.FIXER.name.lower()
    ],
    "replaced_attributes": {
        UltrastarFileAttributes.MP3.name.lower(): UltrastarFileAttributes.AUDIO.name.lower(),
        UltrastarFileAttributes.DUETSINGERP1.name.lower(): UltrastarFileAttributes.P1.name.lower(),
        UltrastarFileAttributes.DUETSINGERP2.name.lower(): UltrastarFileAttributes.P2.name.lower(),
        UltrastarFileAttributes.AUTHOR.name.lower(): UltrastarFileAttributes.CREATOR.name.lower(),
        UltrastarFileAttributes.PREVIEW.name.lower(): UltrastarFileAttributes.PREVIEWSTART.name.lower(),
    }
}


# the regex "^#[a-zA-Z0-9]+:" for ATTRIBUTE would be better fitting for the format up to now but meh
class UltrastarFileRegexMatcher(Enum):
    ATTRIBUTE: str = r"^#\w+:"  # e.g. "#TITLE:"
    # ATTRIBUTE_WITH_BOM_ENCODING: str = r"^\\ufeff#\w+:"  # e.g. "#TITLE:"
    SINGER: str = r"^P\d+$"  # e.g. "P1"
    END_OF_PHRASE: str = r"^- \d+$"  # e.g. "- 5"
    END_OF_FILE: str = r"^E$"  # e.g. "E"
    SING_LINE: str = r"^[:*FRG] \d+ \d+ \d+ "  # e.g. ": 0 1 8 Normal" | "* 0 1 8 Golden" | "F 0 1 8 Freestyle" | "R 0 1 8 Rap" | "G 0 1 8 RapGolden"

