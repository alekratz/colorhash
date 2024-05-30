#!/bin/bash
set -eo pipefail
here="$(dirname "$(realpath "$0")")"

hashes=(md5 sha1 sha224 sha256 sha384 sha512)
matrices=(nibble randomart)

cd "$here/.."

find "examples" -type f -name '*.in' | \
while read infile; do
    for hash in "${hashes[@]}"; do
        for matrix in "${matrices[@]}"; do
            svgfile="examples/$(basename -s .in "$infile")-$hash-$matrix.svg"
            pngfile="examples/$(basename -s .in "$infile")-$hash-$matrix.png"
            echo "Generating $svgfile"
            python3 -m colorhash "$infile" --output-type svg --out "$svgfile" --hash "$hash" --matrix "$matrix"
            echo "Generating $pngfile"
            convert "$svgfile" "$pngfile"
        done
    done
done
