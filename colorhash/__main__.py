"Generate a graphic based on the hash of an input file."

import argparse
import hashlib
from pathlib import Path
import sys

from .colorizer import PaletteColorizer
from .matricizer import Matricizer, NibbleMatricizer, RandomartMatricizer
from .svg import gensvg


# TODO - WASM compile for embedding directly in HTML
# TODO - option to add a caption based on the filename
# TODO - palettes defined by JSON


PALETTES = {
    "red": [f"#{0x110000 * i:06x}" for i in range(0x10)],
    "green": [f"#{0x001100 * i:06x}" for i in range(0x10)],
    "blue": [f"#{0x000011 * i:06x}" for i in range(0x10)],
    "black": [f"#{0x111111 * i:06x}" for i in range(0x10)],
    "cyan": [f"#{0x001111 * i:06x}" for i in range(0x10)],
    "yellow": [f"#{0x111100 * i:06x}" for i in range(0x10)],
    "magenta": [f"#{0x110011 * i:06x}" for i in range(0x10)],
    "white": [f"#{0x111111 * (0xF - i):06x}" for i in range(0x10)],
}


def main() -> None:
    "Main function entrypoint."
    # pylint: disable=invalid-name

    MATRIX_CHOICES = {
        "nibble": "Use each nibble (4 bits) of the hash to generate a matrix",
        "randomart": "Use the SSH 'randomart' algorithm to generate a matrix",
    }
    MATRIX_HELP = "MATRIX STRATEGY (-m, --matrix)\n" + "\n".join(
        f"    {choice} - {desc}" for choice, desc in MATRIX_CHOICES.items()
    )
    PALETTE_CHOICES = [
        "auto",
        "red",
        "green",
        "blue",
        "black",
        "cyan",
        "yellow",
        "magenta",
        "white",
    ]
    PALETTE_HELP = "\n".join(
        [
            "PALETTE CHOICES",
            "    " + ", ".join(PALETTE_CHOICES),
        ]
    )
    HASH_CHOICES = ["md5", "sha1", "sha224", "sha256", "sha384", "sha512"]
    EPILOGUE = "\n\n".join([MATRIX_HELP, PALETTE_HELP])

    progname: str = sys.argv[0]
    if progname.endswith('__main__.py'):
        progname = 'colorhash'

    ap = argparse.ArgumentParser(
        prog=progname,
        description="Create a piece of art based on the hash of a file.",
        epilog=EPILOGUE,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    ap.add_argument(
        "infile",
        type=argparse.FileType("rb"),
        default=sys.stdin,
        help="The input file to use. Set to '-' or blank for STDIN. default: STDIN",
    )
    ap.add_argument(
        "-o",
        "--out",
        metavar="OUTFILE",
        type=Path,
        default="-",
        help="The output file to use. Set to '-' or blank for STDOUT. default: STDOUT",
    )
    ap.add_argument(
        "-m",
        "--matrix",
        metavar="MATRIX",
        choices=MATRIX_CHOICES.keys(),
        default="nibble",
        help="Choose the strategy that turns the hash into a matrix. default: nibble",
    )
    ap.add_argument(
        "-p",
        "--palette",
        metavar="PALETTE",
        choices=PALETTE_CHOICES,
        default="auto",
        help="Choose the palette. default: auto",
    )
    ap.add_argument(
        "-a",  # the "a" is for "algorithm" (since -h is taken)
        "--hash",
        metavar="ALGORITHM",
        choices=HASH_CHOICES,
        default="sha512",
        help="Choose the hash algorithm. default: sha512",
    )
    ap.add_argument(
        "-z",
        "--square-size",
        metavar="PX",
        type=int,
        default=32,
        help="Decide how big the output squares are, in pixels. default: 32",
    )
    args = ap.parse_args()

    ############################################################################
    # End arg parsing
    ############################################################################

    # Get the hash
    # file_digest (I hope) will not load too much into memory
    hashdata = hashlib.file_digest(args.infile, args.hash).digest()

    # Choose the palette
    palette: list[str]
    if args.palette == 'auto':
        palette = list(PALETTES.values())[sum(hashdata) % 8]
    else:
        palette = PALETTES[args.palette]

    # Choose the dimensions and the matricizer
    matricizer: Matricizer
    match args.matrix:
        case 'nibble':
            w, h = NibbleMatricizer.DIMENSIONS[args.hash]
            matricizer = NibbleMatricizer(w, h)
        case 'randomart':
            # 17x9 is what openssh uses
            # TODO - allow configuring dimensions, maybe
            matricizer = RandomartMatricizer(17, 9)
        case _:
            assert False, f"invalid args.matrix: {args.matrix}"

    # Choose the colorizer
    colorizer = PaletteColorizer(palette)

    # Print SVG
    matrix = matricizer.matricize(hashdata)
    colors = colorizer.colorize(matrix)
    svg = gensvg(colors, args.square_size)
    if str(args.out) == '-':
        sys.stdout.write(svg)
    else:
        args.out.write_text(svg)


main()
