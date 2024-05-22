import abc
from typing import Sequence

from .matricizer import Matrix


class Colorizer(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def colorize(self, matrix: Matrix) -> Matrix:
        """
        Colorize a matrix.
        """


Palette = Sequence[str]


class PaletteColorizer(Colorizer):
    def __init__(self, palette: Palette) -> None:
        assert len(palette) == 16, "palette must contain exactly 16 colors"
        self.palette = palette

    def colorize(self, matrix: Matrix) -> Matrix:
        return [[self.palette[v] for v in row] for row in matrix]
