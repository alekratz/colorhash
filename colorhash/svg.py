"SVG-related functions."
from .colorizer import StrMatrix


def gensvg(matrix: StrMatrix, square_size: int) -> str:
    """
    Generate an SVG based on a given matrix.

    :param matrix: the color matrix to generate the SVG for.
    :param square_size: the size of the squares generated, in pixels.
    :returns: the full generated SVG as a string.
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
