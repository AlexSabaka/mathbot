"""Per-template surface-similarity report vs gsm8k via 5-gram Jaccard.

Pipeline:
  1. Load gsm8k train split (~7,473 problems).
  2. Iterate every template in src/templates/.
  3. For each template, render K samples with deterministic seeds.
  4. For each sample, compute max Jaccard similarity vs every gsm8k problem.
  5. Aggregate per template: max_similarity, mean_similarity, top gsm8k neighbor.
  6. Emit JSON sorted by max_similarity desc.
"""

import json
import re
import sys
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
@click.option("--samples-per-template", "k", default=3, show_default=True, help="Renderings per template.")
@click.option("--seed-base", default=0, show_default=True, help="Base seed; sample j uses seed_base+j.")
@click.option("--n-gram", "n_gram", default=5, show_default=True)
@click.option("--top-k", default=50, show_default=True, help="Top-K templates to print to stdout.")
@click.option("--gsm8k-split", default="train", show_default=True)
@click.option(
    "--output", "-o",
    type=click.Path(dir_okay=False, path_type=Path),
    default=Path("contamination.json"),
    show_default=True,
)
def main(
    templates_dir: Path,
    k: int,
    seed_base: int,
    n_gram: int,
    top_k: int,
    gsm8k_split: str,
    output: Path,
) -> None:
    print(f"loading gsm8k ({gsm8k_split} split)...", file=sys.stderr)
    from datasets import load_dataset

    ds = load_dataset("gsm8k", "main", split=gsm8k_split)
    gsm8k_texts = [row["question"] for row in ds]
    print(f"  loaded {len(gsm8k_texts)} gsm8k problems", file=sys.stderr)

    print(f"shingling gsm8k corpus (n={n_gram})...", file=sys.stderr)
    gsm8k_shingles = [shingles(t, n_gram) for t in gsm8k_texts]

    print(f"loading templates from {templates_dir}...", file=sys.stderr)
    templates = load_all_templates(templates_dir)
    tg = TemplateGenerator(templates_dir=templates_dir)
    print(f"  loaded {len(templates)} templates", file=sys.stderr)

    template_records: list[dict] = []
    skipped = 0
    for i, (tpl_id, tpl) in enumerate(sorted(templates.items()), 1):
        if i % 50 == 0 or i == len(templates):
            print(f"  [{i}/{len(templates)}] processed", file=sys.stderr)

        sample_sims: list[float] = []
        sample_top_idx: list[int] = []
        sample_texts: list[str] = []
        for j in range(k):
            try:
                problem = tg._generate_from_template(tpl, seed=seed_base + j, template_path=tpl.file_path)
            except Exception as e:
                skipped += 1
                continue
            text = problem["problem"]
            mb_sh = shingles(text, n_gram)
            best_sim = 0.0
            best_idx = -1
            for gi, g_sh in enumerate(gsm8k_shingles):
                s = jaccard(mb_sh, g_sh)
                if s > best_sim:
                    best_sim = s
                    best_idx = gi
            sample_sims.append(best_sim)
            sample_top_idx.append(best_idx)
            sample_texts.append(text)

        if not sample_sims:
            continue

        max_idx = sample_sims.index(max(sample_sims))
        top_gi = sample_top_idx[max_idx]
        template_records.append(
            {
                "template_id": tpl_id,
                "template_path": str(tpl.file_path.relative_to(REPO_ROOT)) if tpl.file_path else None,
                "samples_compared": len(sample_sims),
                "max_similarity": max(sample_sims),
                "mean_similarity": sum(sample_sims) / len(sample_sims),
                "top_gsm8k_idx": top_gi,
                "top_gsm8k_text": gsm8k_texts[top_gi] if top_gi >= 0 else "",
                "example_mathbot": sample_texts[max_idx],
            }
        )

    template_records.sort(key=lambda r: r["max_similarity"], reverse=True)

    max_sims = [r["max_similarity"] for r in template_records]
    sorted_max = sorted(max_sims)
    summary = {
        "templates_analyzed": len(template_records),
        "templates_skipped": skipped // k if k else 0,
        "samples_per_template": k,
        "mean_max_sim": sum(max_sims) / len(max_sims) if max_sims else 0.0,
        "p50": percentile(sorted_max, 0.50),
        "p95": percentile(sorted_max, 0.95),
        "p99": percentile(sorted_max, 0.99),
        "max": max(max_sims) if max_sims else 0.0,
    }

    report = {
        "config": {
            "samples_per_template": k,
            "seed_base": seed_base,
            "n_gram": n_gram,
            "gsm8k_split": gsm8k_split,
            "gsm8k_size": len(gsm8k_texts),
        },
        "summary": summary,
        "histogram": histogram(max_sims),
        "templates": template_records,
    }

    with open(output, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("\n=== Top templates by max similarity ===")
    for r in template_records[:top_k]:
        print(f"\n[{r['max_similarity']:.3f}] {r['template_id']} (mean={r['mean_similarity']:.3f}, n={r['samples_compared']})")
        print(f"  MB: {r['example_mathbot'][:200]}")
        print(f"  GS: {r['top_gsm8k_text'][:200]}")

    print(
        f"\nwrote {output}; "
        f"templates={summary['templates_analyzed']}, skipped={summary['templates_skipped']}, "
        f"mean_max={summary['mean_max_sim']:.3f}, p95={summary['p95']:.3f}, "
        f"p99={summary['p99']:.3f}, max={summary['max']:.3f}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
