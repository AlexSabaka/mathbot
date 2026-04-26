"""Per-template self-similarity report — find near-duplicate templates.

Pipeline:
  1. Iterate every template in src/templates/.
  2. For each template, render K samples with deterministic seeds.
  3. Per template, take the UNION of all shingles across the K renderings.
     (Capturing both the static scaffolding and the variable surface.)
  4. Pairwise Jaccard between every (a, b) union; record max-neighbor per template
     and a deduplicated top-pairs list.

Use this to surface candidates for pruning before raising the corpus quality bar.
"""

import json
import re
import sys
from itertools import combinations
from pathlib import Path
from typing import Iterable

import click

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.template_generator import TemplateGenerator  # noqa: E402
from src.yaml_loader import load_all_templates  # noqa: E402


_TOKEN_RE = re.compile(r"[a-z0-9]+")


def shingles(text: str, n: int) -> set[tuple[str, ...]]:
    tokens = _TOKEN_RE.findall(text.lower())
    if len(tokens) < n:
        return {tuple(tokens)} if tokens else set()
    return {tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)}


def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 0.0
    union = len(a | b)
    return len(a & b) / union if union else 0.0


def histogram(values: Iterable[float], buckets: int = 20) -> list[dict]:
    arr = [0] * buckets
    for v in values:
        idx = min(int(v * buckets), buckets - 1)
        arr[idx] += 1
    width = 1.0 / buckets
    return [
        {"bucket": f"{i * width:.2f}-{(i + 1) * width:.2f}", "count": arr[i]}
        for i in range(buckets)
    ]


def percentile(sorted_values: list[float], p: float) -> float:
    if not sorted_values:
        return 0.0
    k = (len(sorted_values) - 1) * p
    f = int(k)
    c = min(f + 1, len(sorted_values) - 1)
    if f == c:
        return sorted_values[f]
    return sorted_values[f] + (sorted_values[c] - sorted_values[f]) * (k - f)


@click.command()
@click.option(
    "--templates-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=REPO_ROOT / "src" / "templates",
    show_default=True,
)
@click.option("--samples-per-template", "k", default=3, show_default=True)
@click.option("--seed-base", default=0, show_default=True)
@click.option("--n-gram", "n_gram", default=5, show_default=True)
@click.option("--top-pairs", default=50, show_default=True, help="Top deduplicated pairs to print.")
@click.option(
    "--pair-thresholds",
    default="0.3,0.5,0.7,0.9",
    show_default=True,
    help="Comma-separated thresholds for the pairs-above-X summary counts.",
)
@click.option(
    "--output", "-o",
    type=click.Path(dir_okay=False, path_type=Path),
    default=Path("internal_contamination.json"),
    show_default=True,
)
def main(
    templates_dir: Path,
    k: int,
    seed_base: int,
    n_gram: int,
    top_pairs: int,
    pair_thresholds: str,
    output: Path,
) -> None:
    print(f"loading templates from {templates_dir}...", file=sys.stderr)
    templates = load_all_templates(templates_dir)
    tg = TemplateGenerator(templates_dir=templates_dir)
    print(f"  loaded {len(templates)} templates", file=sys.stderr)

    print(f"rendering each template × {k} seeds and shingling (n={n_gram})...", file=sys.stderr)
    union_shingles: dict[str, set[tuple[str, ...]]] = {}
    example_text: dict[str, str] = {}
    template_path: dict[str, str | None] = {}
    skipped: list[str] = []

    for i, (tpl_id, tpl) in enumerate(sorted(templates.items()), 1):
        if i % 100 == 0 or i == len(templates):
            print(f"  [{i}/{len(templates)}] rendered", file=sys.stderr)
        union: set[tuple[str, ...]] = set()
        first_text: str | None = None
        for j in range(k):
            try:
                problem = tg._generate_from_template(tpl, seed=seed_base + j, template_path=tpl.file_path)
            except Exception:
                continue
            text = problem["problem"]
            if first_text is None:
                first_text = text
            union |= shingles(text, n_gram)
        if not union:
            skipped.append(tpl_id)
            continue
        union_shingles[tpl_id] = union
        example_text[tpl_id] = first_text or ""
        template_path[tpl_id] = (
            str(tpl.file_path.relative_to(REPO_ROOT)) if tpl.file_path else None
        )

    ids = sorted(union_shingles.keys())
    n = len(ids)
    print(f"comparing {n}×{n} pairs ({n * (n - 1) // 2} unordered)...", file=sys.stderr)

    max_neighbor: dict[str, tuple[float, str]] = {tid: (0.0, "") for tid in ids}
    pair_records: list[dict] = []

    for a, b in combinations(ids, 2):
        s = jaccard(union_shingles[a], union_shingles[b])
        if s == 0.0:
            continue
        if s > max_neighbor[a][0]:
            max_neighbor[a] = (s, b)
        if s > max_neighbor[b][0]:
            max_neighbor[b] = (s, a)
        pair_records.append({"a": a, "b": b, "similarity": s})

    pair_records.sort(key=lambda r: r["similarity"], reverse=True)

    template_records = []
    for tid in ids:
        sim, neighbor = max_neighbor[tid]
        template_records.append(
            {
                "template_id": tid,
                "template_path": template_path[tid],
                "max_neighbor_similarity": sim,
                "top_neighbor_id": neighbor or None,
                "top_neighbor_path": template_path.get(neighbor) if neighbor else None,
                "example": example_text[tid],
                "neighbor_example": example_text.get(neighbor, "") if neighbor else "",
            }
        )
    template_records.sort(key=lambda r: r["max_neighbor_similarity"], reverse=True)

    max_sims = [r["max_neighbor_similarity"] for r in template_records]
    sorted_max = sorted(max_sims)

    thresholds = [float(t.strip()) for t in pair_thresholds.split(",") if t.strip()]
    pair_counts_at = {f"≥{t}": sum(1 for r in pair_records if r["similarity"] >= t) for t in thresholds}

    summary = {
        "templates_analyzed": n,
        "templates_skipped": len(skipped),
        "samples_per_template": k,
        "mean_max_neighbor_sim": sum(max_sims) / n if n else 0.0,
        "p50": percentile(sorted_max, 0.50),
        "p95": percentile(sorted_max, 0.95),
        "p99": percentile(sorted_max, 0.99),
        "max": max(max_sims) if max_sims else 0.0,
        "pair_counts": pair_counts_at,
        "total_nonzero_pairs": len(pair_records),
    }

    enriched_top_pairs = [
        {
            **r,
            "a_path": template_path.get(r["a"]),
            "b_path": template_path.get(r["b"]),
            "a_example": example_text.get(r["a"], ""),
            "b_example": example_text.get(r["b"], ""),
        }
        for r in pair_records[:top_pairs]
    ]

    report = {
        "config": {
            "samples_per_template": k,
            "seed_base": seed_base,
            "n_gram": n_gram,
        },
        "summary": summary,
        "histogram": histogram(max_sims),
        "templates": template_records,
        "top_pairs": enriched_top_pairs,
        "skipped": skipped,
    }

    with open(output, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("\n=== Top deduplicated pairs ===")
    for p in enriched_top_pairs:
        print(f"\n[{p['similarity']:.3f}] {p['a']}  ⇄  {p['b']}")
        print(f"  A: {p['a_example'][:180]}")
        print(f"  B: {p['b_example'][:180]}")

    pair_summary = ", ".join(f"{thr}:{n}" for thr, n in pair_counts_at.items())
    print(
        f"\nwrote {output}; templates={n} (skipped={len(skipped)}); "
        f"mean_max={summary['mean_max_neighbor_sim']:.3f}, p95={summary['p95']:.3f}, "
        f"p99={summary['p99']:.3f}, max={summary['max']:.3f}; "
        f"pairs above thresholds: {pair_summary}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
