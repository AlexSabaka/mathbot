"""Mathbot corpus audit package.

Two consumer-facing entrypoints:

- `mathbot lint [PATH]` → `lint_path` (or `lint_corpus` for the default).
- `mathbot health` → `run_health`.

Both ship findings as JSON via [report.py](report.py).
"""

from .contamination import cross_template_contamination
from .coverage import coverage_rows, coverage_summary
from .dupes import (
    density_report, find_near_dupes, flat_difficulty_template_ids,
    normalize_for_dupes,
)
from .findings import Finding, Severity, count_by_severity
from .health import run_health
from .lint import lint_corpus, lint_loaded_templates, lint_path, lint_template
from .render import RenderedSample, first_sample_per_tier, render_samples
from .report import emit_json, lint_report, write_lint_summary


__all__ = [
    # Public types
    "Finding", "Severity", "RenderedSample",
    # Lint API
    "lint_corpus", "lint_loaded_templates", "lint_path", "lint_template",
    # Health API
    "run_health",
    # Render helper
    "first_sample_per_tier", "render_samples",
    # Coverage / health building blocks
    "coverage_rows", "coverage_summary",
    "find_near_dupes", "flat_difficulty_template_ids",
    "normalize_for_dupes", "density_report",
    "cross_template_contamination",
    # Output
    "count_by_severity", "lint_report", "write_lint_summary", "emit_json",
]
