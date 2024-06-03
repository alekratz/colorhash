"All things that turn a numeric matrix into a colored matrix."
from typing import Sequence

from .color import Color
from .matricizer import Matrix
from .palettes import Palette


ColorMatrix = Sequence[Sequence[Color]]


def colorize(palette: Palette, matrix: Matrix) -> ColorMatrix:
    return [[palette[v] for v in row] for row in matrix]
