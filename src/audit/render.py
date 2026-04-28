"""Render-K-samples helper consolidated from the (now-deleted) audit
scripts.

`audit_templates.py` (via `dump_all_samples.py`) and
`internal_contamination.py` both rendered every template with K
deterministic seeds. This module is the single home for that pattern.

Multi-tier templates render once per declared tier so the audit sees
the full spread of problem shapes the corpus can produce — same logic
the legacy `dump_all_samples.py` followed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Tuple

from ..template_generator import TemplateGenerator
from ..yaml_loader import TemplateDefinition


@dataclass
class RenderedSample:
    """One rendered output of a template at a specific (seed, tier) pair."""
    template_id: str
    seed: int
    tier: str
    body: str
    answer: str
    raw: dict


def _tiers(template: TemplateDefinition) -> list[str]:
    """Return the difficulty tiers a template renders at.

    Single-tier → its declared `difficulty`. Multi-tier → every entry
    in `difficulty_tiers`.
    """
    if template.difficulty_tiers:
        return list(template.difficulty_tiers)
    return [template.difficulty]


def render_samples(
    template: TemplateDefinition,
    template_generator: TemplateGenerator,
    samples_per_template: int,
    seed_base: int = 0,
    tiers: Optional[Iterable[str]] = None,
) -> list[RenderedSample]:
    """Render `samples_per_template` outputs per declared tier.

    Returns `samples_per_template * len(tiers)` samples in deterministic
    seed order. Render exceptions are swallowed — the caller decides
    what to do with a template that renders zero samples (typically a
    `render_crash` finding via the lint runner, or a skip in
    contamination).
    """
    tier_names = list(tiers) if tiers is not None else _tiers(template)
    out: list[RenderedSample] = []
    for tier in tier_names:
        for j in range(samples_per_template):
            seed = seed_base + j
            try:
                problem = template_generator._generate_from_template(
                    template,
                    seed=seed,
                    template_path=template.file_path,
                    requested_difficulty=tier,
                )
            except Exception:
                continue
            out.append(RenderedSample(
                template_id=template.id,
                seed=seed,
                tier=tier,
                body=problem.get("problem", ""),
                answer=problem.get("task_params", {}).get("expected_answer", ""),
                raw=problem,
            ))
    return out


def first_sample_per_tier(
    template: TemplateDefinition,
    template_generator: TemplateGenerator,
    seed_base: int = 0,
) -> list[RenderedSample]:
    """Render exactly one sample per tier — the cheap path used by
    coverage / dupe analysis where K samples per template would dominate
    the runtime without changing the answer for those checks.
    """
    return render_samples(
        template, template_generator,
        samples_per_template=1, seed_base=seed_base,
    )
