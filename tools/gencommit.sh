#!/bin/bash
set -eo pipefail
here="$(dirname "$(realpath "$0")")"
cd "$here/.."

echo "Generating examples/commithash.svg"
python3 -m colorhash "$(git rev-parse HEAD)" --input-type hash --hash sha1 --output-type svg --out examples/commithash.svg

