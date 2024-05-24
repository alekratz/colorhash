"Base color palette definitions."
import abc
from typing import Sequence, Self


class Palette(metaclass=abc.ABCMeta):
    """
    A 16-color palette.

    All colors must be HTML color strings.
    """

    @abc.abstractmethod
    def choose(self, color: int) -> str:
        """
        Chooses the given color in this palette.
        """

    def __getitem__(self, color: int) -> str:
        return self.choose(color)


class StaticPalette(Palette):
    """
    A static color palette with discrete colors.
    """

    def __init__(self, colors: Sequence[str]) -> None:
        """
        Creates a new static color palette.

        :param colors: the colors for this palette. Must be exactly 16 colors.
        """
        if len(colors) != 16:
            raise ValueError(f"palette must have exactly 16 colors (got {len(colors)})")
        self.colors = colors

    def choose(self, color: int) -> str:
        if not isinstance(color, int):
            raise KeyError("palette color indices must be an integer")
        return self.colors[color]


DEFAULT_PALETTES = {
    "red": StaticPalette([f"#{0x110000 * i:06x}" for i in range(0x10)]),
    "green": StaticPalette([f"#{0x001100 * i:06x}" for i in range(0x10)]),
    "blue": StaticPalette([f"#{0x000011 * i:06x}" for i in range(0x10)]),
    "black": StaticPalette([f"#{0x111111 * i:06x}" for i in range(0x10)]),
    "cyan": StaticPalette([f"#{0x001111 * i:06x}" for i in range(0x10)]),
    "yellow": StaticPalette([f"#{0x111100 * i:06x}" for i in range(0x10)]),
    "magenta": StaticPalette([f"#{0x110011 * i:06x}" for i in range(0x10)]),
    "white": StaticPalette([f"#{0x111111 * (0xF - i):06x}" for i in range(0x10)]),
}


PALETTES = {**DEFAULT_PALETTES}
