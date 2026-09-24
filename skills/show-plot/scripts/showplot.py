#!/usr/bin/env python3
"""Open image files in Preview on the Mac, or draw them in the terminal.

    showplot.py [--blocks] [--width COLS] PATH [PATH ...]

PATH may be a file, a glob, a directory (its images, newest first), `~/...`, or an Obsidian embed
`![[02-Projects/...png]]` (resolved against ~/brain). By default each file's absolute path is
appended to ~/.showplot/queue, which the Mac-side plotwatch.sh opens in Preview. `--blocks` draws
truecolour half-blocks in this terminal instead.
"""
import argparse
import glob
import os
import re
import shutil
import sys
from pathlib import Path

from PIL import Image

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}
VAULT = Path.home() / "brain"
QUEUE = Path.home() / ".showplot" / "queue"


def resolve(arg: str) -> list[Path]:
    m = re.fullmatch(r"!?\[\[([^\]|]+)(\|[^\]]*)?\]\]", arg.strip())
    if m:
        arg = str(VAULT / m.group(1))
    arg = os.path.expanduser(arg.strip().strip("`'\""))
    p = Path(arg)
    if p.is_dir():
        files = [f for f in p.iterdir() if f.suffix.lower() in IMAGE_EXT]
        return sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)
    hits = [Path(h) for h in sorted(glob.glob(arg))]
    return hits or [p]


def enqueue(path: Path) -> None:
    QUEUE.parent.mkdir(exist_ok=True)
    with QUEUE.open("a") as f:
        f.write(f"{path.resolve()}\n")
    print(path.resolve())


def show_blocks(img: Image.Image, cols: int, rows: int) -> None:
    img = img.convert("RGB")
    w, h = img.size
    width = min(cols, w)
    height = max(2, min(int(round(width * h / w)), 2 * rows))
    width = max(1, int(round(height * w / h))) if height == 2 * rows else width
    px = img.resize((width, height - height % 2), Image.LANCZOS).load()
    lines = []
    for y in range(0, height - height % 2, 2):
        row = []
        for x in range(width):
            (r1, g1, b1), (r2, g2, b2) = px[x, y], px[x, y + 1]
            row.append(f"\x1b[38;2;{r1};{g1};{b1}m\x1b[48;2;{r2};{g2};{b2}m\u2580")
        lines.append("".join(row) + "\x1b[0m")
    sys.stdout.write("\n".join(lines) + "\n")
    sys.stdout.flush()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--blocks", action="store_true", help="draw in this terminal instead of Preview")
    ap.add_argument("--width", type=int, default=None, help="columns (default: the pane's width)")
    args = ap.parse_args()
    size = shutil.get_terminal_size((120, 40))
    cols = args.width or max(10, size.columns - 1)
    status = 0
    for arg in args.paths:
        for path in resolve(arg):
            if not path.is_file():
                print(f"showplot: no such file: {path}", file=sys.stderr)
                status = 1
                continue
            if not args.blocks:
                enqueue(path)
                continue
            print(f"\x1b[1m{path}\x1b[0m")
            with Image.open(path) as img:
                show_blocks(img, cols, max(5, size.lines - 3))
    return status


if __name__ == "__main__":
    sys.exit(main())
