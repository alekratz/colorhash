"All things that turn a numeric matrix into a colored matrix."
import abc
from typing import Sequence

from .matricizer import Matrix


StrMatrix = Sequence[Sequence[str]]


class Colorizer(metaclass=abc.ABCMeta):
    """
    The base Colorizer class.

    A colorizer turns a numeric matrix into a color matrix, colors being represented by strings of
    HTML colors.
    """

    @abc.abstractmethod
    def colorize(self, matrix: Matrix) -> StrMatrix:
        """
        Colorize a matrix.

        :param matrix: the matrix to colorize.
        :returns: the colorized matrix.
        """


Palette = Sequence[str]


class PaletteColorizer(Colorizer):
    """
    A palette colorizer.

    This colorizer will use a palette to colorize its inputs. A palette is 16 colors.
    """
    def __init__(self, palette: Palette) -> None:
        """
        Create a new palette colorizer for a given palette.

        :param palette: the palette to use for this colorizer.
        """
        assert len(palette) == 16, "palette must contain exactly 16 colors"
        self.palette = palette

    def colorize(self, matrix: Matrix) -> StrMatrix:
        """
        Colorize the given matrix using this colorizer's palette.

        :param matrix: the matrix to colorize.
        :returns: the colorized matrix.
        """
        return [[self.palette[v] for v in row] for row in matrix]
