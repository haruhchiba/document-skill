#!/usr/bin/env python3
"""Resolve the local visual-reference library without publishing its images."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


LIBRARY_RELATIVE_PATH = Path(
    "サンプルスライド_20260529_詳細解析"
) / "06_資料作成スキル用テンプレートライブラリ"
REQUIRED_FILES = ("catalog.csv", "catalog.json", "REFERENCE.md")
REQUIRED_DIRS = ("slides", "thumbnails", "contact_sheets")


def is_library(path: Path) -> bool:
    return path.is_dir() and all((path / name).exists() for name in REQUIRED_FILES + REQUIRED_DIRS)


def candidate_paths(explicit: str | None) -> list[Path]:
    candidates: list[Path] = []
    if explicit:
        candidates.append(Path(explicit))
    if env_path := os.environ.get("DOCUMENT_SKILL_REFERENCE_LIBRARY"):
        candidates.append(Path(env_path))
    config_file = Path.home() / ".codex" / "document-skill-reference-library.txt"
    if config_file.is_file():
        configured_path = config_file.read_text(encoding="utf-8").splitlines()
        if configured_path and configured_path[0].lstrip("\ufeff").strip():
            candidates.append(Path(configured_path[0].lstrip("\ufeff").strip()))

    anchors = [Path.cwd(), Path(__file__).resolve().parent]
    for anchor in anchors:
        for parent in (anchor, *anchor.parents):
            candidates.append(parent / LIBRARY_RELATIVE_PATH)
            candidates.append(parent / "assets" / "reference-template-library")
    return candidates


def resolve_library(explicit: str | None) -> Path:
    seen: set[Path] = set()
    for candidate in candidate_paths(explicit):
        resolved = candidate.expanduser().resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if is_library(resolved):
            return resolved
    raise FileNotFoundError(
        "Reference library not found. Pass --library-dir or set "
        "DOCUMENT_SKILL_REFERENCE_LIBRARY."
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library-dir")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--out-file")
    args = parser.parse_args()

    library = resolve_library(args.library_dir)
    if args.out_file:
        output = Path(args.out_file)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(str(library), encoding="utf-8")
    if args.json:
        print(json.dumps({"library_dir": str(library)}, ensure_ascii=False, indent=2))
    elif not args.out_file:
        print(library)


if __name__ == "__main__":
    main()
