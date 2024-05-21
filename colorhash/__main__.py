import hashlib
import sys


# TODO - WASM compile for embedding directly in HTML
# TODO - command line parsing for hash type, infile, forcing a palette, etc
# TODO - file streaming for infile so we aren't loading e.g. 4GB into memory unnecessarily


def hash2matrix(data: bytes, w: int, h: int) -> list[list[int]]:
    """
    Convert a hash to a list of rows of nibbles.
    """
    # Split the data into nibbles first, in case the width is an odd number
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


def gensvg(matrix: list[list[int]], square_size: int = 32):
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


color_table = [
    # red
    [f"#{0x110000 * i:06x}" for i in range(0x10)],
    # green
    [f"#{0x001100 * i:06x}" for i in range(0x10)],
    # blue
    [f"#{0x000011 * i:06x}" for i in range(0x10)],
    # black
    [f"#{0x111111 * i:06x}" for i in range(0x10)],
    # cyan
    [f"#{0x001111 * i:06x}" for i in range(0x10)],
    # yellow
    [f"#{0x111100 * i:06x}" for i in range(0x10)],
    # magenta
    [f"#{0x110011 * i:06x}" for i in range(0x10)],
    # white
    [f"#{0x111111 * (0xF - i):06x}" for i in range(0x10)],
]

dimensions_table = {
    "md5": (8, 4),
    "sha1": (8, 5),
    "sha224": (8, 7),
    "sha256": (8, 8),
    "sha384": (12, 8),
    "sha512": (16, 8),
}


hash_algo = "sha512"

infile = sys.stdin.buffer


if len(sys.argv) > 1:
    inpath = sys.argv[1]
    if inpath != '-':
        infile = open(inpath, 'rb')


hashdata = hashlib.file_digest(infile, hash_algo).digest()
w, h = dimensions_table[hash_algo]
matrix = hash2matrix(hashdata, w, h)

# Print matrix
# pprint.pprint([[hex(c) for c in row] for row in matrix])

palette_no = sum(hashdata) % 8
# print('using palette:', palette_no)
palette = color_table[palette_no]

colors = [[palette[v] for v in row] for row in matrix]

# Print colors
# pprint.pprint([[hex(c) for c in row] for row in colors])

# Print SVG
print(gensvg(colors))
