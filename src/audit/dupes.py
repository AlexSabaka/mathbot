"""Within-cell near-dupe detection + density report.

Ported from the (deleted) `audit_templates.py`. Two related concerns:

1. **Near-dupes**: pairwise SequenceMatcher within the same `(grade,
   topic, family)` cell. Skeleton-normalized text (numbers and
   capitalized words replaced with placeholders) so "Alice 5 apples"
   and "Bob 7 apples" land as a duplicate. Tier-suffix (`__easy`,
   `__medium`, `__hard`) is stripped before pair-matching so multi-tier
   renders of the same source don't trip the detector.

2. **Density**: cell counts, top-N over-densified cells, singleton
   families. The proposal calls out k6 as 33% of the corpus; this is
   the report that surfaces those skews.
"""

from __future__ import annotations

import difflib
import re
from collections import Counter, defaultdict
from typing import Any, Dict, Iterable, List, Tuple

from .checks import (
    DUPE_FLAT_DIFFICULTY_THRESHOLD, DUPE_THRESHOLD, SPEC_MANDATED_FAMILIES,
)
from .render import RenderedSample


_NUM_RE = re.compile(r"-?\$?\d+(?:\.\d+)?%?")
_NAME_RE = re.compile(r"\b[A-Z][a-z]+\b")
_WS_RE = re.compile(r"\s+")


def normalize_for_dupes(text: str) -> str:
    """Reduce a problem statement to its structural skeleton.

    Numbers → `<N>`, capitalized words → `<W>`, whitespace collapsed.
    The same transform is applied to both sides of the comparison so
    over-trigger on sentence-initial words ("Find", "Write") cancels.
    """
    t = _NUM_RE.sub("<N>", text)
    t = _NAME_RE.sub("<W>", t)
    t = _WS_RE.sub(" ", t).strip().lower()
    return t


def _strip_tier_suffix(template_id: str) -> str:
    """Multi-tier renders carry `__easy` / `__medium` / `__hard` on
    their test_id; strip so dupe detection treats them as one source.
    """
    for tier in ("__easy", "__medium", "__hard"):
        if template_id.endswith(tier):
            return template_id[: -len(tier)]
    return template_id


def find_near_dupes(
    samples: Iterable[RenderedSample],
    cell_of: Dict[str, Tuple[str, str, str]],
    complexity_of: Dict[str, int],
    threshold: float = DUPE_THRESHOLD,
) -> List[Dict[str, Any]]:
    """Find near-duplicate pairs within the same `(grade, topic, family)` cell.

    Args:
        samples: rendered outputs (one per template — caller ensures
            single-sample-per-template, otherwise pairs explode).
        cell_of: template_id → `(grade, topic, family)` tuple.
        complexity_of: template_id → 1/2/3 int (used to label the kind
            of duplicate: same-difficulty vs cross-difficulty).
        threshold: SequenceMatcher ratio cutoff.

    Returns rows sorted by similarity desc:
        {pid_a, pid_b, similarity, cell, kind}
    where `kind` ∈ {`same_difficulty`, `cross_difficulty`}.

    Pairs from the same base template (multi-tier renders of one source)
    are skipped — they're *intended* to look alike across tiers.
    """
    by_cell: dict[tuple, list[RenderedSample]] = defaultdict(list)
    for s in samples:
        cell = cell_of.get(s.template_id)
        if cell is not None:
            by_cell[cell].append(s)

    pairs: List[Dict[str, Any]] = []
    for cell, group in by_cell.items():
        if len(group) < 2:
            continue
        norms = [(s, normalize_for_dupes(s.body)) for s in group]
        for i in range(len(norms)):
            for j in range(i + 1, len(norms)):
                a, b = norms[i][0], norms[j][0]
                if _strip_tier_suffix(a.template_id) == _strip_tier_suffix(b.template_id):
                    continue
                ratio = difflib.SequenceMatcher(
                    None, norms[i][1], norms[j][1], autojunk=False,
                ).ratio()
                if ratio < threshold:
                    continue
                comp_a = complexity_of.get(a.template_id)
                comp_b = complexity_of.get(b.template_id)
                kind = (
                    "cross_difficulty"
                    if comp_a is not None and comp_b is not None and comp_a != comp_b
                    else "same_difficulty"
                )
                pairs.append({
                    "pid_a": a.template_id,
                    "pid_b": b.template_id,
                    "similarity": round(ratio, 3),
                    "cell": f"{cell[0]}.{cell[1]}.{cell[2]}",
                    "kind": kind,
                })
    return sorted(pairs, key=lambda r: r["similarity"], reverse=True)


def flat_difficulty_template_ids(pairs: Iterable[Dict[str, Any]]) -> set[str]:
    """Templates that appear in a cross-difficulty pair ≥ flat-threshold.

    These are problems whose difficulty axis is fake — only number
    ranges differ from a different-tier sibling, not problem structure.
    Lint reports them via the `structurally_flat_difficulty` rule.
    """
    flagged: set[str] = set()
    for p in pairs:
        if (
            p["kind"] == "cross_difficulty"
            and p["similarity"] >= DUPE_FLAT_DIFFICULTY_THRESHOLD
        ):
            flagged.add(p["pid_a"])
            flagged.add(p["pid_b"])
    return flagged


def density_report(
    cells_by_template: Iterable[Tuple[str, str, str, str]],  # (tid, grade, topic, family)
) -> Dict[str, Any]:
    """Per-cell counts; top over-densified; singleton families.

    Output shape:
        {
          "top_overdensified_cells": [{cell, count, spec_mandated}, ...],
          "singleton_families": [{family, spec_mandated}, ...],
          "grade_topic_matrix": {(grade, topic): count, ...},
        }
    """
    cell_counter: Counter[Tuple[str, str, str]] = Counter()
    fam_counter: Counter[str] = Counter()
    grade_topic: Counter[Tuple[str, str]] = Counter()

    for _tid, grade, topic, family in cells_by_template:
        cell_counter[(grade, topic, family)] += 1
        fam_counter[family] += 1
        grade_topic[(grade, topic)] += 1

    overdensified = [
        {
            "cell": f"{grade}.{topic}.{family}",
            "count": n,
            "spec_mandated": family in SPEC_MANDATED_FAMILIES,
        }
        for (grade, topic, family), n in cell_counter.most_common(20)
        if n >= 5
    ]
    singletons = [
        {
            "family": fam,
            "spec_mandated": fam in SPEC_MANDATED_FAMILIES,
        }
        for fam, n in sorted(fam_counter.items())
        if n == 1
    ]

    return {
        "top_overdensified_cells": overdensified,
        "singleton_families": singletons,
        "grade_topic_matrix": {f"{g}.{t}": n for (g, t), n in sorted(grade_topic.items())},
    }
