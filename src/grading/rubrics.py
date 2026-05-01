"""Binary rubric items for `mathbot grade`.

12 grade-agnostic items plus 8 K1-specific items, sourced from
[MATHBOT_RUBRICS.md] at the repo root. Each item is a small dataclass
the grader serializes into the prompt and references by `id` when
mapping the model's JSON verdict back to `GradeFinding`s.

`requires_image=True` items are filtered out under `--no-image` runs;
they describe checks (visual presence, visual ↔ prose match, label
overlap) the grader cannot perform without the rasterized figure.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Literal


RubricSet = Literal["agnostic", "k1"]


@dataclass(frozen=True)
class RubricItem:
    """One yes/no rubric criterion."""
    id: str           # e.g. "agnostic.1", "k1.4" — stable across runs
    set: RubricSet
    name: str         # short human-readable label
    prompt: str       # the line(s) inserted into the model prompt
    requires_image: bool = False


# ---------------------------------------------------------------------------
# Grade-agnostic — 12 items applied at every grade.
# ---------------------------------------------------------------------------

AGNOSTIC_ITEMS: List[RubricItem] = [
    RubricItem(
        id="agnostic.1", set="agnostic",
        name="No template-engine leakage",
        prompt=(
            "No template-engine leakage. The rendered output contains no literal "
            "`{{ var }}`, `[a|b|c]`, `{% ... %}`, `<auto>`, or other un-substituted "
            "template syntax."
        ),
    ),
    RubricItem(
        id="agnostic.2", set="agnostic",
        name="No filler boilerplate",
        prompt=(
            "No filler boilerplate. The prose does not contain redundant filler "
            "phrases like \"Please solve this problem\" tacked onto a question that "
            "is already a question."
        ),
    ),
    RubricItem(
        id="agnostic.3", set="agnostic",
        name="Answer matches the question's form",
        prompt=(
            "Answer matches the question's form. The fixture answer matches the form "
            "the question asks for: integer counts for \"how many\", a named option "
            "for \"which\", units consistent with the prose. No tuple/scalar mismatch."
        ),
    ),
    RubricItem(
        id="agnostic.4", set="agnostic",
        name="Subject-verb and article agreement",
        prompt=(
            "Subject-verb and article agreement. Prose obeys English grammar: \"an "
            "eraser\" not \"a eraser\", \"each carton costs\" not \"each cartons "
            "costs\", subjects and verbs agree in number."
        ),
    ),
    RubricItem(
        id="agnostic.5", set="agnostic",
        name="Pronoun consistency",
        prompt=(
            "Pronoun consistency. Pronouns used in prose are consistent with the "
            "named subject and consistent across sentences. A character introduced as "
            "\"Duane\" should not be referred to as \"they\" later (unless the "
            "template uses singular-they consistently throughout)."
        ),
    ),
    RubricItem(
        id="agnostic.6", set="agnostic",
        name="Entity consistency across sentences",
        prompt=(
            "Entity consistency across sentences. Entities in the setup match "
            "entities priced/referenced later. If the prose introduces items A and B, "
            "the math should be about A and B, not about C."
        ),
    ),
    RubricItem(
        id="agnostic.7", set="agnostic",
        name="Not a tautology",
        prompt=(
            "Not a tautology. The prose does not state the answer. If the question is "
            "\"how many clips long is the eraser?\" the prose should not literally "
            "say \"the eraser is 5 clips long\" earlier."
        ),
    ),
    RubricItem(
        id="agnostic.8", set="agnostic",
        name="Not a single-fact recall",
        prompt=(
            "Not a single-fact recall. The problem requires at least one operation, "
            "comparison, or transformation, not just retrieval of a definitional fact "
            "like \"how many days in a week\" — unless the template's family is "
            "explicitly recall-based."
        ),
    ),
    RubricItem(
        id="agnostic.9", set="agnostic",
        name="Skill category matches declared topic",
        prompt=(
            "Skill category matches declared topic. The cognitive work the problem "
            "requires aligns with the topic field. A template under "
            "`measurement.length` should be testing length-measurement, not "
            "language-comprehension of comparative adjectives."
        ),
    ),
    RubricItem(
        id="agnostic.10", set="agnostic",
        name="Math-prose-answer triangle",
        prompt=(
            "Math-prose-answer triangle. The displayed answer is consistent with the "
            "prose setup. Even without re-deriving the math, the order of magnitude "
            "and unit should match what the operations described would produce."
        ),
    ),
    RubricItem(
        id="agnostic.11", set="agnostic",
        name="No unrendered placeholders or N/A values",
        prompt=(
            "No unrendered placeholders or N/A values. Rendered output contains no "
            "\"None\", \"null\", \"undefined\", or \"N/A\" strings where a real "
            "value should be."
        ),
    ),
    RubricItem(
        id="agnostic.12", set="agnostic",
        name="Visual integrity (if visual block present)",
        prompt=(
            "Visual integrity. If a figure is present, it has no overlapping labels, "
            "no labels going off-canvas, no markers placed inconsistently with their "
            "data, and no obvious geometric impossibilities (e.g. closed circuit "
            "labeled \"open\")."
        ),
        requires_image=True,
    ),
]


# ---------------------------------------------------------------------------
# K1-specific — 8 additional items applied only when grade == 1.
# ---------------------------------------------------------------------------

K1_ITEMS: List[RubricItem] = [
    RubricItem(
        id="k1.1", set="k1",
        name="Visual block present",
        prompt=(
            "Visual block present. The template renders a figure. Pure-prose K1 "
            "problems are categorically suspect because most K1 skills are "
            "picture-anchored. Pass = image present."
        ),
        requires_image=True,
    ),
    RubricItem(
        id="k1.2", set="k1",
        name="Visual is load-bearing or prose is sufficient",
        prompt=(
            "Visual is load-bearing or prose is sufficient. Either the figure carries "
            "information needed to solve, OR the prose alone fully specifies the "
            "problem and the figure illustrates appropriately. For topics like "
            "`measurement.length`, `numbers.counting`, `geometry.shapes` the figure "
            "should be primary; cosmetic-only figures fail."
        ),
    ),
    RubricItem(
        id="k1.3", set="k1",
        name="Visual matches prose",
        prompt=(
            "Visual matches prose. If the prose says \"5 clips\" and the figure "
            "shows clips, the figure should show 5 clips. Visual quantity matches "
            "stated quantity."
        ),
        requires_image=True,
    ),
    RubricItem(
        id="k1.4", set="k1",
        name="Prose is brief (≤ ~25 words)",
        prompt=(
            "Prose is brief. The full problem prose (excluding the answer) is under "
            "approximately 25 words. K1 students cannot parse long multi-sentence "
            "narratives. Pass = ≤25 words."
        ),
    ),
    RubricItem(
        id="k1.5", set="k1",
        name="Concrete, age-appropriate nouns",
        prompt=(
            "Concrete, age-appropriate nouns. Entities are concrete, "
            "physically-present-in-a-K1-classroom-or-home objects (apples, ducks, "
            "blocks, clips, pencils, animals, shapes). Not abstract concepts "
            "(investments, rates, percentages, equations)."
        ),
    ),
    RubricItem(
        id="k1.6", set="k1",
        name="Single-step task",
        prompt=(
            "Single-step task. The problem requires one operation or one observation, "
            "not a chain of reasoning. K1 students do not yet do multi-step word "
            "problems."
        ),
    ),
    RubricItem(
        id="k1.7", set="k1",
        name="Numerals within K1 range",
        prompt=(
            "Numerals within K1 range. All numerals shown are within roughly 0–20 "
            "(some curricula extend to 100 for counting). No fractions, no decimals, "
            "no negative numbers."
        ),
    ),
    RubricItem(
        id="k1.8", set="k1",
        name="Answer is a small whole number, single word, or simple shape name",
        prompt=(
            "Answer is a small whole number, single word, or simple shape name. K1 "
            "answers are categorically simple: a count (3), a comparison (\"taller\"), "
            "a shape name (\"circle\"), a position (\"on top\"). Not tuples, not "
            "decimals, not algebraic expressions."
        ),
    ),
]


def items_for(rubric_set: str, with_image: bool) -> List[RubricItem]:
    """Return the active rubric items for a run.

    `rubric_set` is one of "agnostic", "k1", "all". When `with_image` is
    False, items that require seeing the figure (K1.1, K1.3, agnostic
    #12) are dropped — there's nothing to grade them against.
    """
    if rubric_set == "agnostic":
        items = list(AGNOSTIC_ITEMS)
    elif rubric_set == "k1":
        items = list(K1_ITEMS)
    elif rubric_set == "all":
        items = [*AGNOSTIC_ITEMS, *K1_ITEMS]
    else:
        raise ValueError(f"unknown rubric set: {rubric_set!r}")
    if not with_image:
        items = [i for i in items if not i.requires_image]
    return items
