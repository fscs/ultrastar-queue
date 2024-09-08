from enum import Enum


class UltrastarFileRegexMatcher(Enum):
    """
    A helper class used to match the format of a line to an Ultrastar line format.

    Attributes
    ----------
    ATTRIBUTE : str
        The regex for matching an attribute line containing the name of the attribute and the value.
        e.g. '#TITLE:Best Title Ever'
    PLAYER_DELIMITER : str
        The regex for matching a player delimiter line containing the player who has to sing the next lines.
        e.g. 'P1'
    END_OF_PHRASE : str
        The regex for matching a line marking the end of a phrase.
        e.g. '- 5'
    END_OF_FILE : str
        The regex for matching the line marking the end of the file.
        e.g. 'E'
    SING_LINE : str
        The regex for matching a sing line containing lyrics.
        e.g. ': 0 1 8 Normal', '* 0 1 8 Golden', 'F 0 1 8 Freestyle', 'R 0 1 8 Rap', 'G 0 1 8 RapGolden'

    References
    ----------
    The information about the Ultrastar line formats is from
    https://usdx.eu/format/#specs (accessesed at 27.07.2024)
    """

    ATTRIBUTE: str = r"^#\w+:"
    PLAYER_DELIMITER: str = r"^P\d+$"
    END_OF_PHRASE: str = r"^- \d+ ?\d*$"
    END_OF_FILE: str = r"^E$"
    SING_LINE: str = r"^[:*FRG] -?\d+ -?\d+ -?\d+ "
