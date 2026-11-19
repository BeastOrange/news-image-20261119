#!/usr/bin/env python3
"""Entrypoint: reproduce the entry image at /output/entry.png.

Stdlib only. The image is built deterministically by build_image.py and
shipped in this repository as entry.png; this program copies it to the
grader's output directory, byte for byte, so repeated runs are identical.
"""
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> int:
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    out_dir.mkdir(parents=True, exist_ok=True)
    src = HERE / "entry.png"
    dst = out_dir / "entry.png"
    shutil.copyfile(src, dst)
    print(f"wrote {dst} ({dst.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
