"""Coverage matrix — (grade, topic, family, difficulty) → counts.

Ported from the (deleted) `scripts/coverage_matrix.py`. Output is a
list of dict rows; the caller picks JSON / a CSV writer / pivot table.
Sparse: empty cells aren't emitted. Pivot externally to spot gaps.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from ..yaml_loader import TemplateDefinition


def coverage_rows(
    templates: Iterable[TemplateDefinition],
) -> List[Dict[str, Any]]:
    """Bucket templates into (grade, topic, family, difficulty) cells.

    Returns rows sorted by `(grade, topic, family, difficulty)`. Each row:
        {grade: 'k3', topic: 'arithmetic.addition', family: 'addition',
         difficulty: 'easy', count: 4, anchor_count: 1, variant_count: 3}

    Multi-tier templates are counted once per declared tier — they
    occupy multiple cells, since they actually render at each tier.
    """
    cells: Dict[Tuple[str, str, str, str], List[Path]] = defaultdict(list)
    for tpl in templates:
        tiers = tpl.difficulty_tiers or [tpl.difficulty]
        for tier in tiers:
            key = (f"k{tpl.grade}", tpl.topic, tpl.family, tier)
            cells[key].append(tpl.file_path)

    rows: List[Dict[str, Any]] = []
    for (grade, topic, family, difficulty), paths in sorted(cells.items()):
        anchor_count = sum(
            1 for p in paths if p and p.name.endswith("_anchor.yaml")
        )
        rows.append({
            "grade": grade,
            "topic": topic,
            "family": family,
            "difficulty": difficulty,
            "count": len(paths),
            "anchor_count": anchor_count,
            "variant_count": len(paths) - anchor_count,
        })
    return rows


def coverage_summary(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Top-level totals: cells, anchors, variants, total templates."""
    total_anchors = sum(r["anchor_count"] for r in rows)
    total_variants = sum(r["variant_count"] for r in rows)
    return {
        "cells": len(rows),
        "anchors": total_anchors,
        "variants": total_variants,
        "total": total_anchors + total_variants,
    }
