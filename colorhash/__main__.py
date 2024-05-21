import hashlib
import sys

from .hash_colorizer import PaletteColorizer


# TODO - WASM compile for embedding directly in HTML
# TODO - command line parsing for hash type, infile, forcing a palette, etc
# TODO - file streaming for infile so we aren't loading e.g. 4GB into memory unnecessarily
# TODO - option to add a caption based on the filename
# TODO - palettes defined by JSON


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

palette_no = sum(hashdata) % 8
palette = color_table[palette_no]

colorizer = PaletteColorizer(palette)

# Print colors
# pprint.pprint([[hex(c) for c in row] for row in colors])

# Print SVG
print(colorizer.hash_to_svg(hashdata, w, h, 32))
