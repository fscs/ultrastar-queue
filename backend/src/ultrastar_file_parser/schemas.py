from enum import Enum


# from https://usdx.eu/format/#specs accessesed at 27.07.2024
# the regex "^#[a-zA-Z0-9]+:" for ATTRIBUTE would be better fitting for the format up to now but meh
class UltrastarFileRegexMatcher(Enum):
    ATTRIBUTE: str = r"^#\w+:"  # e.g. "#TITLE:"
    SINGER: str = r"^P\d+$"  # e.g. "P1"
    END_OF_PHRASE: str = r"^- \d+ ?\d*$"  # e.g. "- 5"
    END_OF_FILE: str = r"^E$"  # e.g. "E"
    SING_LINE: str = r"^[:*FRG] -?\d+ -?\d+ -?\d+ "  # e.g. ": 0 1 8 Normal" | "* 0 1 8 Golden" | "F 0 1 8 Freestyle" | "R 0 1 8 Rap" | "G 0 1 8 RapGolden"

