"""Corpus-level health report — coverage matrix, density, near-dupes,
internal contamination.

Renders every template with K samples once, then feeds the samples to
the dupe + contamination passes. Coverage and density are derived from
the loaded `TemplateDefinition`s and don't need rendering.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from ..template_generator import TemplateGenerator
from ..yaml_loader import load_all_templates
from .checks import (
    DEFAULT_NGRAM, DEFAULT_PAIR_THRESHOLDS, DEFAULT_SAMPLES,
    DEFAULT_SEED_BASE, DEFAULT_TOP_PAIRS,
)
from .contamination import cross_template_contamination
from .coverage import coverage_rows, coverage_summary
from .dupes import density_report, find_near_dupes
from .render import first_sample_per_tier, render_samples


def run_health(
    templates_dir: Path,
    samples_per_template: int = DEFAULT_SAMPLES,
    seed_base: int = DEFAULT_SEED_BASE,
    top_pairs: int = DEFAULT_TOP_PAIRS,
    n_gram: int = DEFAULT_NGRAM,
    pair_thresholds: tuple = DEFAULT_PAIR_THRESHOLDS,
) -> Dict[str, Any]:
    """Build the full health report.

    Sections:
        coverage: long-format rows + a small summary
        density:  top-overdensified cells, singleton families, grade×topic matrix
        near_dupes: within-cell SequenceMatcher pairs ≥ threshold
        contamination: cross-template Jaccard (K-shingle on K renders)
    """
    templates = load_all_templates(templates_dir)
    template_generator = TemplateGenerator(templates_dir=templates_dir)

    # Cell membership maps (template_id → grade/topic/family tuple, complexity).
    cell_of: Dict[str, tuple] = {}
    complexity_of: Dict[str, int] = {}
    cells_by_template: List[tuple] = []
    diff_to_complexity = {"easy": 1, "medium": 2, "hard": 3}
    for tid, tpl in templates.items():
        cell_of[tid] = (f"k{tpl.grade}", tpl.topic, tpl.family)
        complexity_of[tid] = diff_to_complexity.get(tpl.difficulty, 0)
        cells_by_template.append(
            (tid, f"k{tpl.grade}", tpl.topic, tpl.family),
        )
        # Multi-tier templates: emit one rendered sample row per tier.
        if tpl.difficulty_tiers:
            for tier in tpl.difficulty_tiers:
                tiered_id = f"{tid}__{tier}"
                cell_of[tiered_id] = (f"k{tpl.grade}", tpl.topic, tpl.family)
                complexity_of[tiered_id] = diff_to_complexity.get(tier, 0)

    # Single rendering pass — we need:
    #   - 1 sample per (template, tier) for dupes (cheap; widens cells too much otherwise)
    #   - K samples per (template, tier) for contamination (richer surface)
    one_sample = []
    k_samples = []
    for tpl in templates.values():
        one_sample.extend(first_sample_per_tier(tpl, template_generator, seed_base=seed_base))
        k_samples.extend(render_samples(
            tpl, template_generator,
            samples_per_template=samples_per_template, seed_base=seed_base,
        ))

    # For dupes, label samples by their tiered id when multi-tier so
    # `find_near_dupes` cell membership lookup works for tier-suffixed ids.
    for s in one_sample:
        tpl = templates.get(s.template_id)
        if tpl and tpl.difficulty_tiers:
            s.template_id = f"{s.template_id}__{s.tier}"

    return {
        "coverage": {
            "summary": coverage_summary(coverage_rows(templates.values())),
            "rows": coverage_rows(templates.values()),
        },
        "density": density_report(cells_by_template),
        "near_dupes": find_near_dupes(one_sample, cell_of, complexity_of),
        "contamination": cross_template_contamination(
            k_samples,
            n_gram=n_gram,
            top_pairs=top_pairs,
            pair_thresholds=pair_thresholds,
        ),
    }
