from enum import Enum


class Modes(Enum):
    """enum class containing songbirdcore modes"""

    ALBUM = "album"
    """Specifies album mode"""
    SONG = "song"
    """Specifies song mode"""


def get_mode_values():
    return [e.value for e in Modes]
