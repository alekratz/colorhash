"Colorhash writer classes"
import abc
import zlib

from .color import Color, ColorMatrix


class Writer(metaclass=abc.ABCMeta):
    """
    Base writer class.

    This is used to write an input colorized matrix to a string, which is then forwarded to the
    appropriate output.
    """

    @abc.abstractmethod
    def write(self, matrix: ColorMatrix) -> bytes:
        """
        Write the color matrix to a string.

        :param matrix: the color matrix to generate the image for.
        :returns: the generated image as a string.
        """


class ANSIWriter(Writer):
    """
    ANSI terminal writer. This will output a 24-bit true color string.
    """

    def write(self, matrix: ColorMatrix) -> bytes:
        """
        Write the color matrix to an ANSI string.

        :param matrix: the color matrix to generate the SVG for.
        :returns: the full generated SVG as a string.
        """
        esc = "\x1b"
        reset = f"{esc}[0m"
        c = "██"

        def ansi_color(c: Color) -> str:
            c = c.to_rgb()
            return f"{esc}[38;2;{round(c.r)};{round(c.g)};{round(c.b)}m"

        out = ""
        for row in matrix:
            for col in row:
                out += ansi_color(col)
                out += c
            out += "\n"
        out += reset
        return out.encode()


class SVGWriter(Writer):
    """
    SVG string writer.
    """

    def __init__(self, square_size: int) -> None:
        """
        Create a new SVG writer that uses the given square size.

        :param square_size: the size of the squares generated, in pixels.
        """
        self.square_size = square_size

    def write(self, matrix: ColorMatrix) -> bytes:
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
        return svg.encode()


class PNGWriter(Writer):
    def __init__(self, square_size: int) -> None:
        """
        Create a new PNG writer that uses the given square size.

        :param square_size: the size of the squares generated, in pixels.
        """
        self.square_size = square_size

    def write(self, matrix: ColorMatrix) -> bytes:
        """
        Generate a PNG based on a given matrix.

        :param matrix: the color matrix to generate the SVG for.
        :returns: the full generated PNG as an ASCII-encoded string. It's probably a good idea to
                  convert this to bytes since it's binary data being shoved into a string type.
        """
        w = self.square_size * len(matrix[0])
        h = self.square_size * len(matrix)

        def i32(i: int) -> bytes:
            return int.to_bytes(i, 4, "big")

        def chunk(name: str, data: bytes) -> bytes:
            assert len(name) == 4, "chunk name must be exactly 4 bytes"
            chunk = bytearray()
            chunk += i32(len(data))
            # add the name to the data so it also gets encoded with the crc32
            data = name.encode('ascii') + data
            chunk += data
            chunk += i32(zlib.crc32(data))
            return bytes(chunk)

        # Convert the matrix into RGB byte triples
        colors = [
            [
                bytes([int(c.r), int(c.g), int(c.b)])
                for c in map(lambda c: c.to_rgb(), row)
            ]
            for row in matrix
        ]

        # Create the palette based on the unique colors available
        # NOTE : these could be done in the same dict and would probably save a little bit of
        # memory, however, mypy likes it when we keep types easy
        pal2col = {}
        col2pal = {}
        for i, c in enumerate(set(sum(colors, []))):
            pal2col[i] = c
            col2pal[c] = i

        assert len(pal2col) // 2 < 16, "palette for PNG image was longer than 16 colors"

        # Header
        png = bytearray([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])

        # write the IHDR chunk
        png += chunk(
            "IHDR",
            # width, height, bit depth (4), color type (3, palette),
            # compression method (always 0), filter method (always 0),
            # interlace method (0, not interlaced)
            i32(w) + i32(h) + bytes([4, 3, 0, 0, 0]),
        )
        # write the palette chunk
        png += chunk(
            "PLTE",
            b"".join([pal2col[i] for i in range(len(pal2col))]),
        )
        # create scanlines and shove them into IDAT chunks
        idat = bytearray()
        for row in colors:
            line = bytearray([0])
            for col in row:
                b = (col2pal[col] << 4) | col2pal[col]
                # add square_size number of colors (divided by 2, since we only need 4 bits per
                # color)
                for _ in range(self.square_size // 2):
                    line += bytes([b])
            # add square_size number of lines
            for _ in range(self.square_size):
                idat += line
        # write the IDAT chunk
        png += chunk("IDAT", zlib.compress(idat))
        # write the IEND chunk
        png += chunk("IEND", bytes())
        return png
