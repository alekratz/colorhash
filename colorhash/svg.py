from .matricizer import Matrix


def gensvg(matrix: Matrix, square_size: int) -> str:
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
