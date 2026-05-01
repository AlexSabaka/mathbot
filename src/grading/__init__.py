"""Mathbot template-quality grading via local VLM.

Experimental v1 — `mathbot grade` calls a locally-running Ollama
instance to apply a binary rubric ([MATHBOT_RUBRICS.md]) to rendered
templates. Each rubric item produces one `GradeFinding` per (template,
seed) so authors can see exactly which seed surfaced an issue, mirroring
the `mathbot lint` output shape.
"""

from .findings import GradeFinding, count_by_severity
from .grader import grade_corpus, grade_template
from .rubrics import AGNOSTIC_ITEMS, K1_ITEMS, RubricItem, items_for


__all__ = [
    "GradeFinding",
    "count_by_severity",
    "grade_corpus",
    "grade_template",
    "AGNOSTIC_ITEMS",
    "K1_ITEMS",
    "RubricItem",
    "items_for",
]
