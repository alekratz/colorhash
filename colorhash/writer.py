import abc

from .color import Color, ColorMatrix


class Writer(metaclass=abc.ABCMeta):
    """
    Base writer class.

    This is used to write an input colorized matrix to a string, which is then forwarded to the
    appropriate output.
    """

    @abc.abstractmethod
    def write(self, matrix: ColorMatrix) -> str:
        "Write the color matrix to a string."


class ANSIWriter(Writer):
    def write(self, matrix: ColorMatrix) -> str:
        ESC = "\x1b"
        RESET = f"{ESC}[0m"
        C = "██"

        def ansi_color(c: Color) -> str:
            c = c.to_rgb()
            return f"{ESC}[38;2;{round(c.r)};{round(c.g)};{round(c.b)}m"

        out = ""
        for row in matrix:
            for col in row:
                out += ansi_color(col)
                out += C
            out += "\n"
        out += RESET
        return out


class SVGWriter(Writer):
    def __init__(self, square_size: int) -> None:
        """
        Create a new SVG writer that uses the given square size.

        :param square_size: the size of the squares generated, in pixels.
        """
        self.square_size = square_size

    def write(self, matrix: ColorMatrix) -> str:
        """
        Generate an SVG based on a given matrix.

        :param matrix: the color matrix to generate the SVG for.
        :returns: the full generated SVG as a string.
        """
        h = len(matrix)
        w = len(matrix[0])

        # Start SVG string
        svg = f'<svg width="{w * self.square_size}" height="{h * self.square_size}" xmlns="http://www.w3.org/2000/svg">\n'

        # Generate grid
        for r in range(h):
            for c in range(w):
                x = c * self.square_size
                y = r * self.square_size
                color = matrix[r][c]
                svg += f'  <rect x="{x}" y="{y}" width="{self.square_size}" height="{self.square_size}" fill="{color.to_html_color()}" />\n'

        # Close SVG string
        svg += "</svg>"
        return svg
