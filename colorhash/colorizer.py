import abc
from typing import Sequence

from .matricizer import Matrix


StrMatrix = Sequence[Sequence[str]]


class Colorizer(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def colorize(self, matrix: Matrix) -> StrMatrix:
        """
        Colorize a matrix.
        """


Palette = Sequence[str]


class PaletteColorizer(Colorizer):
    def __init__(self, palette: Palette) -> None:
        assert len(palette) == 16, "palette must contain exactly 16 colors"
        self.palette = palette

    def colorize(self, matrix: Matrix) -> StrMatrix:
        return [[self.palette[v] for v in row] for row in matrix]
