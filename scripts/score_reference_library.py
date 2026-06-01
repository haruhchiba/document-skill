#!/usr/bin/env python3
"""Score every visual-reference slide against each output-slide role."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


NUMERIC_RANGES = {
    "brightness": 255.0,
    "contrast": 100.0,
    "white_ratio": 1.0,
    "dark_ratio": 1.0,
    "edge_density": 30.0,
    "saturation": 1.0,
}


def split_values(value: str) -> set[str]:
    return {item.strip() for item in (value or "").split(",") if item.strip()}


def numeric_similarity(row: dict[str, str], targets: dict[str, float]) -> tuple[float, list[str]]:
    total = 0.0
    reasons: list[str] = []
    for key, target in targets.items():
        if key not in NUMERIC_RANGES or not row.get(key):
            continue
        actual = float(row[key])
        similarity = max(0.0, 1.0 - abs(actual - float(target)) / NUMERIC_RANGES[key])
        points = similarity * 12.0
        total += points
        reasons.append(f"{key}={actual:g}近似+{points:.1f}")
    return total, reasons


def score_row(row: dict[str, str], slide_spec: dict) -> tuple[float, list[str]]:
    score = 0.0
    reasons: list[str] = []
    categories = set(slide_spec.get("primary_categories", []))
    layouts = set(slide_spec.get("layout_families", []))
    preferred_tags = set(slide_spec.get("preferred_tags", []))
    avoid_tags = set(slide_spec.get("avoid_tags", []))
    auto_categories = set(slide_spec.get("auto_categories", []))
    semantic = split_values(row.get("semantic_categories", ""))
    tags = split_values(row.get("tags", ""))

    if row.get("primary_category") in categories:
        score += 55
        reasons.append("primary_category一致+55")
    semantic_matches = categories & semantic
    if semantic_matches:
        points = min(18, len(semantic_matches) * 9)
        score += points
        reasons.append(f"semantic一致+{points}")
    if row.get("layout_family") in layouts:
        score += 22
        reasons.append("layout_family一致+22")
    if row.get("auto_category") in auto_categories:
        score += 10
        reasons.append("auto_category一致+10")
    tag_matches = preferred_tags & tags
    if tag_matches:
        points = min(18, len(tag_matches) * 6)
        score += points
        reasons.append(f"preferred_tags一致+{points}")
    avoided = avoid_tags & tags
    if avoided:
        points = min(24, len(avoided) * 8)
        score -= points
        reasons.append(f"avoid_tags該当-{points}")

    visual_score, visual_reasons = numeric_similarity(row, slide_spec.get("visual_targets", {}))
    score += visual_score
    reasons.extend(visual_reasons)
    return round(score, 3), reasons


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", required=True)
    parser.add_argument("--spec", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--top-k", type=int, default=5)
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(args.catalog, encoding="utf-8-sig", newline="") as handle:
        catalog = list(csv.DictReader(handle))
    with open(args.spec, encoding="utf-8") as handle:
        spec = json.load(handle)

    all_scores: list[dict] = []
    shortlists: list[dict] = []
    for slide_spec in spec["slides"]:
        ranked = []
        for row in catalog:
            score, reasons = score_row(row, slide_spec)
            record = {
                "output_slide": slide_spec["slide"],
                "role": slide_spec["role"],
                "reference_id": row["id"],
                "score": score,
                "primary_category": row.get("primary_category", ""),
                "layout_family": row.get("layout_family", ""),
                "tags": row.get("tags", ""),
                "slide_path": row.get("slide_path", ""),
                "thumbnail_path": row.get("thumbnail_path", ""),
                "reasons": " | ".join(reasons),
            }
            all_scores.append(record)
            ranked.append(record)
        ranked.sort(key=lambda item: (-item["score"], item["reference_id"]))
        shortlists.append(
            {
                "output_slide": slide_spec["slide"],
                "role": slide_spec["role"],
                "candidates": ranked[: args.top_k],
            }
        )

    fieldnames = list(all_scores[0].keys())
    with open(out_dir / "reference-score-all.csv", "w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_scores)
    with open(out_dir / "reference-shortlist.json", "w", encoding="utf-8") as handle:
        json.dump(
            {
                "catalog_rows": len(catalog),
                "output_slides": len(spec["slides"]),
                "scored_pairs": len(all_scores),
                "top_k": args.top_k,
                "shortlists": shortlists,
            },
            handle,
            ensure_ascii=False,
            indent=2,
        )
        handle.write("\n")

    print(
        json.dumps(
            {
                "catalog_rows": len(catalog),
                "output_slides": len(spec["slides"]),
                "scored_pairs": len(all_scores),
                "top_k": args.top_k,
                "out_dir": str(out_dir.resolve()),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
