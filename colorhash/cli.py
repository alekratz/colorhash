"Main driver for the colorhash program."
import argparse
import hashlib
from pathlib import Path
import sys
import textwrap

from .color import colorize
from .matricizer import Matricizer, NibbleMatricizer, RandomartMatricizer
from .palettes import Palette, PALETTES
from .writer import ANSIWriter, SVGWriter, Writer


# TODO - option to add a caption based on the filename (for SVG)
# TODO - load palettes from a file
# TODO - PNG output
# TODO - fix Matricizer.choose_dimensions - either get rid of it or use it


def cli_main() -> None:
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
            "\n".join(
                textwrap.wrap(
                    ", ".join(PALETTE_CHOICES),
                    initial_indent="    ",
                    subsequent_indent="    ",
                )
            ),
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
    OUTPUT_TYPE_CHOICES = {
        "ansi": "the output should be colored for ANSI terminals using 24 bit true color",
        "svg": "the output should be an SVG format",
    }
    OUTPUT_TYPE_HELP = "OUTPUT TYPE (-y, --output-type)\n" + "\n".join(
        [f"     {choice} - {desc}" for choice, desc in OUTPUT_TYPE_CHOICES.items()]
    )
    EPILOGUE = "\n\n".join(
        [MATRIX_HELP, PALETTE_HELP, INPUT_TYPE_HELP, OUTPUT_TYPE_HELP]
    )

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
        "--svg-square-size",
        metavar="PX",
        type=int,
        default=32,
        help="For SVG outputs, decide how big the output squares are, in pixels. default: 32",
    )
    ap.add_argument(
        "-x",
        "--input-type",
        default="path",
        choices=INPUT_TYPE_CHOICES.keys(),
        help="Determines how the input should be treated. default: path",
    )
    ap.add_argument(
        "-y",
        "--output-type",
        default="ansi",
        choices=OUTPUT_TYPE_CHOICES.keys(),
        help="Determines how the output should be generated. default: ansi",
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
            hashdata = hashlib.file_digest(infile, args.hash).digest()  # type: ignore
            # NOTE : previous line has typing ignored because file_digest requires a
            # "_BytesIOLike | _FileDigestFileObj", both of which look like API leaks. Specifying
            # infile to be BinaryIO is not enough and causes the same error.
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

    # Choose the dimensions and the matricizer
    matricizer: Matricizer
    match args.matrix:
        case "nibble":
            matricizer = NibbleMatricizer()
        case "randomart":
            matricizer = RandomartMatricizer()
        case _:
            assert False, f"invalid args.matrix: {args.matrix}"

    # Choose the palette
    palette: Palette
    if args.palette == "auto":
        palette = matricizer.choose_palette(hashdata)
    else:
        palette = PALETTES[args.palette]

    # Matricize and colorize
    matrix = matricizer.matricize(hashdata)
    colors = colorize(palette, matrix)

    # Choose the output writer
    writer: Writer
    match args.output_type:
        case "ansi":
            writer = ANSIWriter()
        case "svg":
            writer = SVGWriter(args.svg_square_size)

    output = writer.write(colors)

    if str(args.out) == "-":
        sys.stdout.write(output)
    else:
        args.out.write_text(output)
