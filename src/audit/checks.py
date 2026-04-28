"""Constants for audit rules — patterns, thresholds, slug canon.

Ported faithfully from the legacy [audit_templates.py](../../audit_templates.py)
(deleted with this phase). Kept centralized so rule authors find the
knobs in one place.
"""

from __future__ import annotations

import re

# Spec-mandated families from MATHBOT_PROBLEMS_PROPOSAL.md, section 1.3.
# Templates matching these are flagged in density reports as
# "spec-mandated" so cull-suggestions skip them.
SPEC_MANDATED_FAMILIES = frozenset({
    "area_perimeter_chain", "compound_growth", "multi_person_sharing",
    "sequential_purchase", "rate_time",
})

# Slug normalization. Any active mismatch fires `slug_noncanonical`.
# 5.7A landed the shapes_2d / shapes_3d fix; this dict is the seed for
# future renames.
SLUG_CANONICAL: dict[str, str] = {
    # "shapes2d": "shapes_2d",  # already migrated; left as a reminder
}

# Unit-format inconsistency patterns. Surfaces "spelled cubic"/"spelled
# squared" forms in problem text — Phase 5.7A unified on m²/m³ but
# variants may slip in. Used by `lint.check_units` over rendered output.
UNIT_INCONSISTENT_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(
        r"\bcubic\s+(cm|m|mm|km|in|ft|meters?|millimeters?|kilometers?)\b",
        re.IGNORECASE,
    ), "spelled_cubic"),
    (re.compile(
        r"\bsquare(d)?\s+(cm|m|mm|km|in|ft|meters?|millimeters?|kilometers?)\b",
        re.IGNORECASE,
    ), "spelled_squared"),
]

# GSM8K-saturation patterns called out in the proposal (section 1.2).
# Each match raises an `info`-severity finding — concentration of these
# patterns within a (grade, topic) cell signals an authoring smell.
GSM8K_SATURATION_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(
        r"\$\s*\d+\s*(bill|note)?\b.*\bchange\b|\bpaid (with|using).*\$",
        re.IGNORECASE,
    ), "money_change"),
    (re.compile(
        r"\bplus\s+\w*\s*tax\b|\bsales\s+tax\b|\b\d+%\s+tax\b",
        re.IGNORECASE,
    ), "with_tax"),
    (re.compile(
        r"\bif\s+\d+\s+(\w+\s+){0,3}cost\b|\bat\s+\$\d+\s+each\b",
        re.IGNORECASE,
    ), "items_at_price_each"),
]

# SequenceMatcher threshold for within-cell near-dupe detection. Tuned
# to catch "Alice 5 apples / Bob 7 apples" twins without flooding on
# incidental phrasing overlap.
DUPE_THRESHOLD = 0.85

# A cross-difficulty pair this similar means the difficulty axis is
# fake — only number ranges differ, not problem structure. Surfaces as
# a per-template `structurally_flat_difficulty` flag.
DUPE_FLAT_DIFFICULTY_THRESHOLD = 0.95

# Surface-length sanity on rendered prompt body. Catches accidental
# double-renders or concatenated test instructions.
LONG_PROMPT_CHARS = 800

# Render-driven lint defaults. K=4 seeds catches most surface bugs
# without being slow on the full corpus (~5s for 640 templates).
DEFAULT_SAMPLES = 4
DEFAULT_SEED_BASE = 0

# Internal-contamination defaults.
DEFAULT_NGRAM = 5
DEFAULT_TOP_PAIRS = 50
DEFAULT_PAIR_THRESHOLDS: tuple[float, ...] = (0.3, 0.5, 0.7, 0.9)
