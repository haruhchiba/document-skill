#!/usr/bin/env python3
"""Build visual comparison sheets from reference-shortlist.json."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps


THUMB_SIZE = (640, 360)
LABEL_HEIGHT = 42
PADDING = 20


def load_thumbnail(library_dir: Path, candidate: dict) -> Image.Image:
    relative_path = candidate.get("thumbnail_path") or candidate["slide_path"]
    image = Image.open(library_dir / relative_path).convert("RGB")
    return ImageOps.contain(image, THUMB_SIZE)


def build_sheet(library_dir: Path, shortlist: dict, out_dir: Path, columns: int) -> Path:
    candidates = shortlist["candidates"]
    rows = math.ceil(len(candidates) / columns)
    tile_w = THUMB_SIZE[0] + PADDING * 2
    tile_h = THUMB_SIZE[1] + LABEL_HEIGHT + PADDING * 2
    sheet = Image.new("RGB", (tile_w * columns, tile_h * rows), "white")
    draw = ImageDraw.Draw(sheet)

    for index, candidate in enumerate(candidates):
        x = (index % columns) * tile_w + PADDING
        y = (index // columns) * tile_h + PADDING
        thumb = load_thumbnail(library_dir, candidate)
        image_x = x + (THUMB_SIZE[0] - thumb.width) // 2
        image_y = y + LABEL_HEIGHT
        sheet.paste(thumb, (image_x, image_y))
        label = (
            f"ID {candidate['reference_id']} | score {candidate['score']} | "
            f"{candidate.get('primary_category', '')}"
        )
        draw.text((x, y + 8), label, fill="black")
        draw.rectangle(
            (x, image_y, x + THUMB_SIZE[0], image_y + THUMB_SIZE[1]),
            outline="#B8B8B8",
            width=2,
        )

    slide = int(shortlist["output_slide"])
    output = out_dir / f"slide-{slide:02d}-candidates.jpg"
    sheet.save(output, quality=92)
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shortlist", required=True)
    parser.add_argument("--library-dir", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--columns", type=int, default=2)
    args = parser.parse_args()

    if args.columns < 1:
        raise ValueError("--columns must be at least 1")

    library_dir = Path(args.library_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(args.shortlist, encoding="utf-8") as handle:
        payload = json.load(handle)

    outputs = [
        str(build_sheet(library_dir, shortlist, out_dir, args.columns))
        for shortlist in payload["shortlists"]
    ]
    print(json.dumps({"generated": outputs}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
