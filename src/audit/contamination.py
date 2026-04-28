"""Cross-template internal contamination via K-shingle Jaccard.

Ported from the (deleted) `scripts/internal_contamination.py`. For
each template, take the UNION of K-shingles across K renderings —
captures both static scaffolding and variable surface — then compute
pairwise Jaccard. Surfaces near-duplicate template *sources* (not just
rendered text) so authors know which templates are basically the same
problem from the model's perspective.
"""

from __future__ import annotations

import re
from itertools import combinations
from typing import Any, Dict, Iterable, List, Tuple

from .checks import DEFAULT_NGRAM, DEFAULT_PAIR_THRESHOLDS, DEFAULT_TOP_PAIRS
from .render import RenderedSample


_TOKEN_RE = re.compile(r"[a-z0-9]+")


def shingles(text: str, n: int) -> set[Tuple[str, ...]]:
    tokens = _TOKEN_RE.findall(text.lower())
    if len(tokens) < n:
        return {tuple(tokens)} if tokens else set()
    return {tuple(tokens[i: i + n]) for i in range(len(tokens) - n + 1)}


def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 0.0
    union = len(a | b)
    return len(a & b) / union if union else 0.0


def percentile(sorted_values: List[float], p: float) -> float:
    if not sorted_values:
        return 0.0
    k = (len(sorted_values) - 1) * p
    f = int(k)
    c = min(f + 1, len(sorted_values) - 1)
    if f == c:
        return sorted_values[f]
    return sorted_values[f] + (sorted_values[c] - sorted_values[f]) * (k - f)


def histogram(values: Iterable[float], buckets: int = 20) -> List[Dict[str, Any]]:
    arr = [0] * buckets
    for v in values:
        idx = min(int(v * buckets), buckets - 1)
        arr[idx] += 1
    width = 1.0 / buckets
    return [
        {"bucket": f"{i * width:.2f}-{(i + 1) * width:.2f}", "count": arr[i]}
        for i in range(buckets)
    ]


def template_unions(
    samples: Iterable[RenderedSample], n_gram: int,
) -> Dict[str, set[Tuple[str, ...]]]:
    """Per template_id, union the K-shingles across all rendered samples.

    Strips the multi-tier `__<tier>` suffix so multi-tier renders fold
    into one source — a multi-tier template is one source, even though
    its samples carry distinct tier-suffixed ids.
    """
    out: Dict[str, set[Tuple[str, ...]]] = {}
    for s in samples:
        base = _strip_tier_suffix(s.template_id)
        out.setdefault(base, set()).update(shingles(s.body, n_gram))
    return out


def _strip_tier_suffix(template_id: str) -> str:
    for tier in ("__easy", "__medium", "__hard"):
        if template_id.endswith(tier):
            return template_id[: -len(tier)]
    return template_id


def cross_template_contamination(
    samples: Iterable[RenderedSample],
    n_gram: int = DEFAULT_NGRAM,
    top_pairs: int = DEFAULT_TOP_PAIRS,
    pair_thresholds: Iterable[float] = DEFAULT_PAIR_THRESHOLDS,
) -> Dict[str, Any]:
    """Pairwise Jaccard across all templates.

    Returns:
        {
          "summary": {templates_analyzed, mean_max_neighbor_sim, p50, p95,
                       p99, max, total_nonzero_pairs, pair_counts},
          "histogram": [...],
          "top_pairs": [{a, b, similarity}, ...],
          "templates": [{template_id, max_neighbor_similarity,
                          top_neighbor_id}, ...],
        }
    """
    unions = template_unions(samples, n_gram)
    ids = sorted(unions.keys())
    n = len(ids)

    max_neighbor: Dict[str, Tuple[float, str]] = {tid: (0.0, "") for tid in ids}
    pair_records: List[Dict[str, Any]] = []
    for a, b in combinations(ids, 2):
        s = jaccard(unions[a], unions[b])
        if s == 0.0:
            continue
        if s > max_neighbor[a][0]:
            max_neighbor[a] = (s, b)
        if s > max_neighbor[b][0]:
            max_neighbor[b] = (s, a)
        pair_records.append({"a": a, "b": b, "similarity": round(s, 4)})

    pair_records.sort(key=lambda r: r["similarity"], reverse=True)
    max_sims = [max_neighbor[tid][0] for tid in ids]
    sorted_max = sorted(max_sims)

    template_records = [
        {
            "template_id": tid,
            "max_neighbor_similarity": max_neighbor[tid][0],
            "top_neighbor_id": max_neighbor[tid][1] or None,
        }
        for tid in ids
    ]
    template_records.sort(
        key=lambda r: r["max_neighbor_similarity"], reverse=True,
    )

    pair_counts_at = {
        f"≥{t}": sum(1 for r in pair_records if r["similarity"] >= t)
        for t in pair_thresholds
    }

    return {
        "summary": {
            "templates_analyzed": n,
            "mean_max_neighbor_sim": (sum(max_sims) / n) if n else 0.0,
            "p50": percentile(sorted_max, 0.50),
            "p95": percentile(sorted_max, 0.95),
            "p99": percentile(sorted_max, 0.99),
            "max": max(max_sims) if max_sims else 0.0,
            "total_nonzero_pairs": len(pair_records),
            "pair_counts": pair_counts_at,
        },
        "histogram": histogram(max_sims),
        "top_pairs": pair_records[:top_pairs],
        "templates": template_records,
    }
