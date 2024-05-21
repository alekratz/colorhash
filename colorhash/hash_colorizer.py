import abc
from typing import Sequence


Matrix = Sequence[Sequence[int]]


class HashColorizer(metaclass=abc.ABCMeta):
    def hash_to_matrix(self, data: bytes, w: int, h: int) -> Matrix:
        """
        Convert a set of bytes to a list of rows of nibbles.
        """

        nibbles = []
        for b in data:
            top = (b & 0xF0) >> 4
            bottom = b & 0x0F
            nibbles += [top, bottom]

        if len(nibbles) != w * h:
            raise ValueError(
                f"input data length ({len(nibbles)}) must match matrix dimensions ({w}x{h} = {w * h})"
            )

        cols = []
        row = []
        for b in nibbles:
            row += [b]
            if len(row) == w:
                cols += [row]
                row = []

        return cols

    @abc.abstractmethod
    def colorize(self, matrix: Matrix) -> Matrix:
        """
        Colorize a matrix.
        """

    def gensvg(self, matrix: Matrix, square_size: int) -> str:
        """
        Generate an SVG based on a given matrix.
        """
        h = len(matrix)
        w = len(matrix[0])

        # Start SVG string
        svg = f'<svg width="{w * square_size}" height="{h * square_size}" xmlns="http://www.w3.org/2000/svg">\n'

        # Generate grid
        for r in range(h):
            for c in range(w):
                x = c * square_size
                y = r * square_size
                color = matrix[r][c]
                svg += f'  <rect x="{x}" y="{y}" width="{square_size}" height="{square_size}" fill="{color}" />\n'

        # Close SVG string
        svg += "</svg>"
        return svg

    def hash_to_svg(self, hash: bytes, w: int, h: int, square_size: int) -> str:
        matrix = self.hash_to_matrix(hash, w, h)
        colors = self.colorize(matrix)
        return self.gensvg(colors, square_size)


Palette = list


class PaletteColorizer(HashColorizer):
    def __init__(self, palette: Palette) -> None:
        assert len(palette) == 16, "palette must contain exactly 16 colors"
        self.palette = palette

    def colorize(self, matrix: Matrix) -> Matrix:
        return [[self.palette[v] for v in row] for row in matrix]
