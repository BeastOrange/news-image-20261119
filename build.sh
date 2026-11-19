#!/bin/sh
# Rebuild the entry image and reproduce it to /output/entry.png.
set -e
cd "$(dirname "$0")"
python3 build_image.py
python3 main.py
