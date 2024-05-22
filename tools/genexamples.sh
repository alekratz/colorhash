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
            outfile="examples/$(basename -s .in "$infile")-$hash-$matrix.svg"
            echo "Generating $outfile"
            python3 -m colorhash "$infile" --out "$outfile" --hash "$hash" --matrix "$matrix"
        done
    done
done
