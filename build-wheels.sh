#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${OUTPUT_DIR:-$ROOT_DIR/dist}"
BUILD_SDIST="${BUILD_SDIST:-0}"

cd "$ROOT_DIR"

python3 -m pip install -U build cibuildwheel twine

rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

if [[ "$BUILD_SDIST" == "1" ]]; then
  python3 -m build --sdist --outdir "$OUTPUT_DIR"
fi

python3 -m cibuildwheel --output-dir "$OUTPUT_DIR"
