"Generate a graphic based on the hash of an input file."

import argparse
import hashlib
from pathlib import Path
import sys
import textwrap

from .colorizer import PaletteColorizer
from .matricizer import Matricizer, NibbleMatricizer, RandomartMatricizer
from .palettes import DEFAULT_PALETTES, PALETTES
from .svg import gensvg


# TODO - WASM compile for embedding directly in HTML
# TODO - option to add a caption based on the filename
# TODO - load palettes from a file
# TODO - better dimensions for randomart matricizer


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
    ] + list(PALETTES.keys())
    PALETTE_HELP = "\n".join(
        [
            "PALETTE CHOICES",
            '\n'.join(textwrap.wrap(
                ", ".join(PALETTE_CHOICES),
                initial_indent="    ",
                subsequent_indent="    ",
            )),
        ]
    )
    HASH_CHOICES = ["md5", "sha1", "sha224", "sha256", "sha384", "sha512"]
    INPUT_TYPE_CHOICES = {
        "path": "the input should be treated as a path and data is read from the path",
        "hash": "the input should be treated as a hexadecimal hash (requires -a or --hash to be supplied)",
        "data": "the input should be treated as raw data",
    }
    INPUT_TYPE_HELP = "INPUT TYPE (-x, --input-type)\n" + "\n".join(
        [f"    {choice} - {desc}" for choice, desc in INPUT_TYPE_CHOICES.items()]
    )
    EPILOGUE = "\n\n".join([MATRIX_HELP, PALETTE_HELP, INPUT_TYPE_HELP])

    progname: str = sys.argv[0]
    if progname.endswith("__main__.py"):
        progname = "colorhash"

    ap = argparse.ArgumentParser(
        prog=progname,
        description="Create a piece of art based on the hash of a file.",
        epilog=EPILOGUE,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    ap.add_argument(
        "input",
        type=str,
        default="-",
        help="The input to use. When acting as a path, set to '-' or blank for STDIN. Use -x or --input-type to control how input is treated. default: -",
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
        # default="sha512",
        required=False,
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
    ap.add_argument(
        "-x",
        "--input-type",
        default="path",
        choices=INPUT_TYPE_CHOICES.keys(),
        help="Determines how the input should be treated. default: path",
    )
    args = ap.parse_args()

    ############################################################################
    # End arg parsing
    ############################################################################

    # -a/--hash arg is not required when we're using file and data input types. only required for
    # hash input type
    if args.input_type in ("data", "path") and args.hash is None:
        args.hash = "sha512"

    # Get the hash
    match args.input_type:
        case "path":
            if args.input == "-":
                infile = sys.stdin.buffer
            else:
                # TODO - pretty error message for when the file doesn't exist
                infile = open(args.input, "rb")
            # file_digest (I hope) will not load too much into memory
            hashdata = hashlib.file_digest(infile, args.hash).digest()
        case "hash":
            # TODO - maybe a better error message?
            if args.hash is None:
                print(
                    "ERROR: -a or --hash should be supplied on the command line when using the hash input type",
                    file=sys.stderr,
                )
                raise SystemExit(1)
            # TODO - pretty error message for malformed input
            hashdata = bytes([int(byte, 16) for byte in textwrap.wrap(args.input, 2)])
        case "data":
            hashdata = hashlib.new(args.hash, args.input.encode()).digest()
        case _:
            assert False, f"unknown input type {args.input_type}"

    # Choose the palette
    palette: list[str]
    if args.palette == "auto":
        palette = list(DEFAULT_PALETTES.values())[sum(hashdata) % len(DEFAULT_PALETTES)]
    else:
        palette = PALETTES[args.palette]

    # Choose the dimensions and the matricizer
    matricizer: Matricizer
    match args.matrix:
        case "nibble":
            w, h = NibbleMatricizer.DIMENSIONS[args.hash]
            matricizer = NibbleMatricizer(w, h)
        case "randomart":
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
    if str(args.out) == "-":
        sys.stdout.write(svg)
    else:
        args.out.write_text(svg)


main()
