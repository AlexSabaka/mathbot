"""Per-template lint rules.

Each rule is a small function returning `list[Finding]`. The rule
runner (`lint_template`) renders K samples once and feeds them to all
render-output rules, so the rendering cost is paid per-template, not
per-rule.

Schema-level rules (`schema_invalid`, `solution_syntax`, `unit_*`) are
already enforced by `YAMLLoader.load_template`; this module wraps that
layer's errors as findings so the lint output is uniform. The lint
runner's `load_template_for_lint` returns a `(template, findings)`
pair — a `None` template plus a `schema_invalid` finding when the YAML
itself is unloadable.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from xml.etree import ElementTree

from ..jinja_renderer import JinjaRenderer
from ..solution_evaluator import execute_solution, format_answer, compare_answers
from ..template_generator import TemplateGenerator
from ..variable_generator import VariableGenerator
from ..yaml_loader import TemplateDefinition, YAMLLoader, load_all_templates
from .checks import (
    DEFAULT_SAMPLES, DEFAULT_SEED_BASE,
    GSM8K_SATURATION_PATTERNS, LONG_PROMPT_CHARS,
    SLUG_CANONICAL, UNIT_INCONSISTENT_PATTERNS,
)
from .findings import Finding
from .render import RenderedSample, render_samples


# ---------------------------------------------------------------------------
# Loader wrapper — surface schema errors as findings.
# ---------------------------------------------------------------------------

def load_template_for_lint(
    path: Path,
) -> Tuple[Optional[TemplateDefinition], List[Finding]]:
    """Load a template, returning (template, findings).

    Schema errors become `schema_invalid` findings. Warnings become
    info-level findings. A template that fails to load returns
    (None, [...errors...]) so the caller can record them and skip
    further rules.
    """
    rel = _relpath(path)
    loader = YAMLLoader()
    template = loader.load_template(path)
    findings: List[Finding] = []
    template_id = template.id if template else path.stem

    for err in loader.errors:
        findings.append(Finding(
            rule="schema_invalid", severity="error",
            template_id=template_id, file=rel, message=err,
        ))
    for warn in loader.warnings:
        findings.append(Finding(
            rule="schema_warning", severity="warning",
            template_id=template_id, file=rel, message=warn,
        ))
    return template, findings


# ---------------------------------------------------------------------------
# Render-output rules. Each takes one RenderedSample and the template.
# ---------------------------------------------------------------------------

_JINJA_LITERAL_RE = re.compile(r"\{\{[^}]+\}\}")


def check_unrendered_jinja(sample: RenderedSample, template: TemplateDefinition) -> List[Finding]:
    if _JINJA_LITERAL_RE.search(sample.body) or _JINJA_LITERAL_RE.search(sample.answer):
        return [Finding(
            rule="unrendered_jinja", severity="error",
            template_id=template.id, file=_relpath(template.file_path),
            seed=sample.seed,
            message=("rendered output contains literal {{...}} — a solution-derived "
                     "variable likely needs `{% set %}` at the top of the template"),
        )]
    return []


def check_empty_answer(sample: RenderedSample, template: TemplateDefinition) -> List[Finding]:
    if not sample.answer.strip():
        return [Finding(
            rule="empty_answer", severity="error",
            template_id=template.id, file=_relpath(template.file_path),
            seed=sample.seed, message="rendered answer is empty",
        )]
    return []


def check_body_too_long(sample: RenderedSample, template: TemplateDefinition) -> List[Finding]:
    n = len(sample.body)
    if n > LONG_PROMPT_CHARS:
        return [Finding(
            rule="body_too_long", severity="warning",
            template_id=template.id, file=_relpath(template.file_path),
            seed=sample.seed,
            message=f"rendered body is {n} chars (limit {LONG_PROMPT_CHARS})",
            extra={"chars": n},
        )]
    return []


def check_units(sample: RenderedSample, template: TemplateDefinition) -> List[Finding]:
    blob = f"{sample.body} {sample.answer}"
    out: List[Finding] = []
    for pat, label in UNIT_INCONSISTENT_PATTERNS:
        m = pat.search(blob)
        if m:
            out.append(Finding(
                rule=f"unit_{label}", severity="warning",
                template_id=template.id, file=_relpath(template.file_path),
                seed=sample.seed,
                message=f"inconsistent unit form in rendered output: {m.group(0)!r}",
            ))
    return out


def check_gsm8k_saturation(sample: RenderedSample, template: TemplateDefinition) -> List[Finding]:
    out: List[Finding] = []
    for pat, label in GSM8K_SATURATION_PATTERNS:
        if pat.search(sample.body):
            out.append(Finding(
                rule=f"gsm8k_{label}", severity="info",
                template_id=template.id, file=_relpath(template.file_path),
                seed=sample.seed,
                message=f"matches GSM8K saturation pattern '{label}'",
            ))
    return out


def check_answer_units_match_topic(
    sample: RenderedSample, template: TemplateDefinition,
) -> List[Finding]:
    fam = template.family
    ans = sample.answer
    if fam.endswith("_area") or fam == "area":
        if not re.search(r"²|\^2|square|sq\.?", ans, re.I) and re.search(r"\d", ans):
            return [Finding(
                rule="area_no_squared_unit", severity="info",
                template_id=template.id, file=_relpath(template.file_path),
                seed=sample.seed,
                message="area answer lacks a squared unit (²/^2/square)",
            )]
    if "volume" in fam:
        if (
            not re.search(r"³|\^3|cubic", ans, re.I)
            and re.search(r"\d\s*(cm|m|mm|in|ft|l|ml)\b", ans, re.I)
        ):
            return [Finding(
                rule="volume_no_cubed_unit", severity="info",
                template_id=template.id, file=_relpath(template.file_path),
                seed=sample.seed,
                message="volume answer lacks a cubed unit (³/^3/cubic)",
            )]
    return []


# ---------------------------------------------------------------------------
# Schema-derived rules (no rendering required).
# ---------------------------------------------------------------------------

def check_slug_canon(template: TemplateDefinition) -> List[Finding]:
    if template.family in SLUG_CANONICAL:
        canonical = SLUG_CANONICAL[template.family]
        return [Finding(
            rule="slug_noncanonical", severity="warning",
            template_id=template.id, file=_relpath(template.file_path),
            message=f"family '{template.family}' should be '{canonical}'",
        )]
    return []


def check_noop_clauses_no_slot(template: TemplateDefinition) -> List[Finding]:
    """Phase β (H3). Templates declaring `noop_clauses:` must reference
    `{{ noop_clause }}` somewhere in `template:`, otherwise the
    `inject_noop=True` path silently no-ops.

    Error severity: a `noop_clauses:` declaration without a slot is a
    bug — fixtures generated with `--noop` will be byte-identical to
    those without and the GSM-NoOp eval signal disappears. Catch it
    early instead of letting it slip through to a benchmark run.
    """
    if not template.noop_clauses:
        return []
    body = template.template
    if "{{ noop_clause }}" in body or "{{noop_clause}}" in body:
        return []
    return [Finding(
        rule="noop_clauses_no_slot", severity="error",
        template_id=template.id, file=_relpath(template.file_path),
        message=(
            "metadata.noop_clauses is non-empty but template body has no "
            "`{{ noop_clause }}` slot — the clause would never render."
        ),
    )]


def check_track_missing(template: TemplateDefinition) -> List[Finding]:
    """Phase α (B2). Flag K9+ templates lacking `metadata.track`.

    K1–K8 templates can omit `track:` because the v2 eval-slicing scheme
    only matters above the universal-arithmetic band. K9+ templates need
    one of {core, advanced, tertiary, US-emphasized} so eval can slice
    out the CCSS-core view from the tertiary-flavoured tail.

    Info-severity only — authors aren't blocked, but `mathbot lint`
    surfaces unset templates so they get filled in during the next
    touch.
    """
    if template.grade < 9:
        return []
    if template.track is not None:
        return []
    return [Finding(
        rule="track_missing", severity="info",
        template_id=template.id, file=_relpath(template.file_path),
        message=(
            f"K{template.grade} template missing `metadata.track`. "
            f"Set to one of: core, advanced, tertiary, US-emphasized."
        ),
    )]


# ---------------------------------------------------------------------------
# γ.3 (A.4) lint rules
# ---------------------------------------------------------------------------

# Numeric content inside `<text>` — both decimals (37.85) and integers
# (94). The post-filter (`_is_axis_label_artifact`) decides per-form
# whether the value is artifact-y. Integers under 10 short-circuit to
# OK so a counting axis (0, 1, 2, …) doesn't false-positive.
_AXIS_LABEL_RE = re.compile(r">(-?\d+(?:\.\d+)?)<")

# Filler phrases that pad a problem question without adding signal.
# Lower-cased; substring match against rendered prose. Each is a
# template-author antipattern (rubric item 2).
_FILLER_BOILERPLATE_PATTERNS = (
    "please solve this problem",
    "please solve the problem",
    "solve the problem.",
    "solve this problem.",
    "find the answer.",
    "find the solution.",
    "compute the answer.",
    "calculate the answer.",
    "what is the answer?",
)

# Tokens that surface as raw Python / null-ish literals when a
# variable misses or formatting falls through. Matched as standalone
# tokens (word boundary) so "Anonymous" doesn't trip "None".
_NONE_LITERAL_RE = re.compile(
    r"\b(None|null|undefined|N/A)\b",
)

# Substrings in problem prose that imply the figure is load-bearing.
_FIGURE_REFERENCE_PHRASES = (
    "shown in the figure",
    "shown below",
    "shown above",
    "the figure shows",
    "the figure below",
    "the figure above",
    "the diagram below",
    "the diagram above",
    "the diagram shows",
    "as shown",
    "as in the figure",
    "as in the diagram",
    "(see figure",
    "(see diagram",
    "see the figure",
    "see the diagram",
    "marked on the figure",
    "marked on the diagram",
    "labelled on the figure",
    "labelled on the diagram",
    "labeled on the figure",
    "labeled on the diagram",
    "the schematic below",
    "the schematic shows",
)


def check_axis_range_artifact(
    sample_visual_svg: str, template: TemplateDefinition,
) -> List[Finding]:
    """γ.3 (A.4) + γ.4q (Q.3). Flag visuals whose axis labels are un-round.

    Auto-fitted axes in PlotSVG / FunctionGraphFigure produce ugly bound
    labels like "37.85", "34.62", or integer "94" when the data range
    lands on un-round numbers. The fix is to pass ``round_to=`` (Q.1)
    or override ``y_range`` explicitly — but only after the lint
    surfaces it.

    Heuristic: scan rendered ``<text>`` contents for numerics; for each,
    apply :func:`_is_axis_label_artifact`. Decimals: strip trailing
    zeros and flag when ≥2 decimal digits remain. Integers: flag when
    |value| ≥ 10 AND value isn't a round multiple. Restricted to SVGs
    that contain a ``<polyline>`` (i.e., plot-shaped visuals); table /
    schematic SVGs use the same `<text>` element type but their cell
    values aren't axis labels and shouldn't be linted by this rule.

    Warning severity.
    """
    if not sample_visual_svg or "<polyline" not in sample_visual_svg:
        return []
    raw = _AXIS_LABEL_RE.findall(sample_visual_svg)
    artifacts = [v for v in raw if _is_axis_label_artifact(v)]
    if not artifacts:
        return []
    # Dedupe + cap for readability.
    deduped = sorted(set(artifacts))
    return [Finding(
        rule="axis_range_artifact", severity="warning",
        template_id=template.id, file=_relpath(template.file_path),
        message=(
            f"visual has decimal label(s) with ≥2 significant decimal "
            f"digits: {deduped[:5]}"
            f"{'...' if len(deduped) > 5 else ''}. Consider overriding "
            f"x_range / y_range or rounding marker values to multiples "
            f"of 0.5 / 1 / 5 / 10."
        ),
    )]


def _is_axis_label_artifact(label: str) -> bool:
    """Return True when ``label`` would read as un-round on an axis.

    Two branches:

    * **Decimals** (``"37.85"``): strip trailing zeros from the decimal
      part; flag when ≥2 non-zero decimal digits remain. ``"1.50"`` →
      ``"1.5"`` → ok; ``"37.85"`` → 2 digits → fire.
    * **Integers** (``"94"``, ``"18"``): γ.4q-extension. Flag when
      |value| ≥ 10 AND value isn't a multiple of any of {5, 10, 25,
      50, 100, 250, 500, 1000}. Catches the cooling template's
      auto-fitted (18, 94) bounds without firing on round bounds
      like (0, 100) or (50, 200). Single-digit values (0–9) stay
      safe because counting axes (0/1/2/…) routinely use them.
    """
    if "." in label:
        _, dec_part = label.split(".", 1)
        trimmed = dec_part.rstrip("0")
        return len(trimmed) >= 2
    try:
        v = int(label)
    except ValueError:
        return False
    av = abs(v)
    if av < 10:
        return False
    for step in (5, 10, 25, 50, 100, 250, 500, 1000):
        if av % step == 0:
            return False
    return True


def check_filler_boilerplate(
    sample: RenderedSample, template: TemplateDefinition,
) -> List[Finding]:
    """γ.4q (Q.3) — flag rubric item 2 (filler phrases).

    The rendered prose contains a redundant filler phrase like
    "Please solve this problem" tacked onto a question that's
    already a question. Substring match against a closed catalogue
    of known offenders (case-insensitive).

    Info severity. The K1-K8 corpus has ~270 templates carrying
    "Please solve this problem." literally — pre-existing quality
    debt that will be cleaned up in γ.5. Surfacing the count
    without flooding the warning channel keeps γ.4q-blocking
    findings (axis artifacts, schematic contradictions) visible.
    Authors fix by deleting the filler from the `template:` block;
    the prose stays the same minus the padding.
    """
    body_lower = sample.body.lower()
    hits = [p for p in _FILLER_BOILERPLATE_PATTERNS if p in body_lower]
    if not hits:
        return []
    return [Finding(
        rule="filler_boilerplate", severity="info",
        template_id=template.id, file=_relpath(template.file_path),
        message=(
            f"rendered prose contains filler phrase(s) {hits!r}. The "
            f"question is already a question — drop the redundant "
            f"closer. Rubric item 2."
        ),
    )]


def check_none_in_output(
    sample: RenderedSample, template: TemplateDefinition,
) -> List[Finding]:
    """γ.4q (Q.3) — flag rubric item 11 (None / null / undefined / N/A).

    Catches templates where a variable misses or the formatter falls
    through and a Python literal surfaces in the rendered output. Word-
    boundary match so "Anonymous" / "Nullable" don't false-positive.

    Warning severity. The fix is template-side: tighten the variable
    spec, add a default, or fix the formatter dispatch.
    """
    out: List[Finding] = []
    rel = _relpath(template.file_path)
    for source_label, content in (("body", sample.body), ("answer", sample.answer)):
        if not content:
            continue
        m = _NONE_LITERAL_RE.search(content)
        if m:
            out.append(Finding(
                rule="none_in_output", severity="warning",
                template_id=template.id, file=rel,
                message=(
                    f"rendered {source_label} contains literal "
                    f"{m.group(0)!r} — likely a missing variable / "
                    f"formatter fallthrough. Rubric item 11."
                ),
            ))
            # One finding per content slot is enough; further hits
            # don't add diagnostic value.
            break  # only the first content slot reports
    return out


def check_visual_prose_contradiction(
    sample: RenderedSample, template: TemplateDefinition,
) -> List[Finding]:
    """γ.3 (A.4). Token-level prose ↔ alt-text consistency check.

    Heuristic: extract the longest content-bearing nouns from the
    visual's alt_text (length ≥ 5 chars, ≤ 12 chars, lowercase
    alphabetic). At least one of them should appear in the problem
    prose; otherwise the alt-text is describing something different
    from what the prose talks about. This is the lightweight version
    — γ.δ's grader skill does the semantic check.

    Skipped when the template has no visual or no alt_text.
    Info severity (not warning) — false-positive rate too high to
    block authors. Use as a "did you forget to update one when you
    edited the other?" signal.
    """
    if template.visual is None or not (template.visual.alt_text or ""):
        return []
    body_lower = sample.body.lower()
    # Tokenise alt_text into candidate keywords.
    alt_lower = template.visual.alt_text.lower()
    tokens = re.findall(r"[a-z]{5,12}", alt_lower)
    if not tokens:
        return []
    # Drop stop-ish words a high-school problem alt-text routinely
    # carries that wouldn't be content-bearing in the prose.
    _STOP = {
        "above", "below", "between", "across", "along", "around",
        "shows", "showing", "shown", "marked", "labeled", "labelled",
        "horizontal", "vertical", "starting", "approaching", "decaying",
        "asymptotically", "toward", "configuration", "diagram", "figure",
        "schematic", "right", "after", "value", "values", "point",
        "point ",
    }
    candidates = [t for t in set(tokens) if t not in _STOP]
    if not candidates:
        return []
    if any(c in body_lower for c in candidates):
        return []
    return [Finding(
        rule="visual_prose_contradiction", severity="info",
        template_id=template.id, file=_relpath(template.file_path),
        message=(
            f"visual.alt_text describes nouns not present in the "
            f"problem prose: {candidates[:5]}. Either the alt text or "
            f"the prose may be out of sync with the figure."
        ),
    )]


def check_simplification_lift_missing(template: TemplateDefinition) -> List[Finding]:
    """γ.3 (A.4). Multi-tier simplifications must vary by tier.

    The point of ``simplifications:`` (γ.1 A.3) is the per-tier
    suppression — at easy tier the template states an assumption,
    at hard tier the same line is suppressed. A multi-tier template
    that ships ``simplifications:`` but with every entry's ``omit_at``
    identical (or empty) doesn't actually exercise the difficulty
    lever, so the field is dead weight.

    Warning severity: the template still loads fine, but the author
    intended a structural-difficulty signal that doesn't exist.
    """
    if not template.simplifications:
        return []
    if not template.difficulty_tiers or len(template.difficulty_tiers) < 2:
        return []  # Single-tier — suppression-by-tier doesn't apply.
    omit_sets = {tuple(sorted(s.omit_at or [])) for s in template.simplifications}
    if len(omit_sets) >= 2:
        return []
    # All entries share the same omit_at set → no per-tier lift.
    return [Finding(
        rule="simplification_lift_missing", severity="warning",
        template_id=template.id, file=_relpath(template.file_path),
        message=(
            f"metadata.simplifications has {len(template.simplifications)} "
            f"entry/entries but every `omit_at` is identical "
            f"({list(omit_sets)[0]}); no tier lift between "
            f"{template.difficulty_tiers}. Either drop the field, or vary "
            f"`omit_at` so the hard tier suppresses what easy/medium states."
        ),
    )]


def check_figure_load_inconsistent(
    sample: RenderedSample, template: TemplateDefinition,
) -> List[Finding]:
    """γ.3 (A.4). Prose ↔ figure_load consistency.

    Two complementary contradictions:

    - Prose says "as shown in the figure" / "the diagram below shows"
      / "see the figure" but ``figure_load: decorative`` (or the field
      is unset on a template *with* a visual) → contradiction:
      either upgrade ``figure_load`` to ``partial`` / ``load_bearing``,
      or drop the prose hook so the solver doesn't expect to find
      information on the figure that isn't there.
    - Template has no ``visual:`` block but ``figure_load`` is set
      to anything other than ``none`` → contradiction.

    Warning severity. Per the seed's "promote to error in Phase ε
    after the corpus settles" — for now, surfaceable but non-blocking.
    """
    declared = _resolve_figure_load(template, sample.tier)
    body_lower = sample.body.lower()
    has_figure_phrase = any(p in body_lower for p in _FIGURE_REFERENCE_PHRASES)

    out: List[Finding] = []
    rel = _relpath(template.file_path)

    if has_figure_phrase and template.visual is None:
        out.append(Finding(
            rule="figure_load_inconsistent", severity="warning",
            template_id=template.id, file=rel,
            message=(
                "prose references a figure ('shown in the figure', "
                "'see the diagram', etc.) but the template has no "
                "`visual:` block. Either remove the prose hook or "
                "add the visual."
            ),
        ))
        return out

    if template.visual is not None:
        if has_figure_phrase and declared == "decorative":
            out.append(Finding(
                rule="figure_load_inconsistent", severity="warning",
                template_id=template.id, file=rel,
                message=(
                    f"prose references the figure but figure_load="
                    f"'decorative' for tier '{sample.tier}'. Upgrade "
                    f"figure_load to 'partial' or 'load_bearing' or drop "
                    f"the figure-reference phrasing."
                ),
            ))
        if declared == "none":
            out.append(Finding(
                rule="figure_load_inconsistent", severity="warning",
                template_id=template.id, file=rel,
                message=(
                    f"figure_load='none' for tier '{sample.tier}' but the "
                    f"template ships a `visual:` block. Either drop the "
                    f"visual or upgrade figure_load."
                ),
            ))
    return out


def check_feature_declared_but_unused(template: TemplateDefinition) -> List[Finding]:
    """γ.3 (A.4). Surface schema features that nothing exercises.

    Two patterns today:

    - ``noop_clauses:`` declared but no fixture passes ``inject_noop=True``.
      The fixtures table doesn't carry that flag yet, so the proxy is
      "the deprecation status alone" — surfaced as a separate info
      finding so authors migrate to ``simplifications:`` instead.
    - ``simplifications:`` declared on a multi-tier template but the
      fixture set covers only one tier. The lift can't possibly be
      exercised by tests.

    Info severity: dead-feature declarations are hygiene issues, not
    bugs.
    """
    out: List[Finding] = []
    rel = _relpath(template.file_path)

    if template.simplifications and template.difficulty_tiers:
        fixture_tiers = {
            (t.difficulty or template.difficulty) for t in template.tests
        }
        # Drop None entries (no tier set + single-tier template).
        fixture_tiers.discard(None)
        active_tiers = set(template.difficulty_tiers)
        if active_tiers and not (active_tiers <= fixture_tiers):
            missing = sorted(active_tiers - fixture_tiers)
            out.append(Finding(
                rule="feature_declared_but_unused", severity="info",
                template_id=template.id, file=rel,
                message=(
                    f"metadata.simplifications declared but tier(s) "
                    f"{missing} have no fixture exercising the "
                    f"per-tier lift. Add a fixture per tier so the "
                    f"suppression behaviour is regression-tested."
                ),
            ))
    return out


def _resolve_figure_load(
    template: TemplateDefinition, tier: Optional[str],
) -> Optional[str]:
    """Resolve `metadata.figure_load` to the active value for ``tier``.

    Returns one of {none, decorative, partial, load_bearing} or
    ``None`` when the field is unset.
    """
    fl = template.figure_load
    if fl is None:
        return None
    if isinstance(fl, str):
        return fl
    if isinstance(fl, dict):
        if tier and tier in fl:
            return fl[tier]
        # No per-tier hit — fall back to the template's default tier.
        return fl.get(template.difficulty)
    return None


def check_steps_ops_consistency(template: TemplateDefinition) -> List[Finding]:
    out: List[Finding] = []
    # Operations we report come from the rendered output's task_params,
    # but `metadata.steps` is fixed on the template. Pull operations from
    # solution code text — same heuristic the generator uses.
    operations = _extract_operations(template.solution)
    if template.steps == 0 and operations and operations != ["arithmetic"]:
        out.append(Finding(
            rule="zero_steps_with_ops", severity="warning",
            template_id=template.id, file=_relpath(template.file_path),
            message=f"metadata.steps=0 but solution declares operations: {operations}",
        ))
    if template.steps > 12:
        out.append(Finding(
            rule="very_high_step_count", severity="warning",
            template_id=template.id, file=_relpath(template.file_path),
            message=f"metadata.steps={template.steps} is unusually high",
        ))
    return out


def _extract_operations(solution_code: str) -> list[str]:
    """Match the heuristic in TemplateGenerator._extract_operations."""
    operations = []
    if "+" in solution_code:
        operations.append("addition")
    if "-" in solution_code:
        operations.append("subtraction")
    if "*" in solution_code:
        operations.append("multiplication")
    if "/" in solution_code:
        operations.append("division")
    if "**" in solution_code or "pow(" in solution_code:
        operations.append("exponentiation")
    if "%" in solution_code:
        operations.append("modulo")
    return operations or ["arithmetic"]


def check_anchor_filename_mismatch(
    template: TemplateDefinition, anchor_ids_by_cell: Dict[Tuple, str],
) -> List[Finding]:
    """Filename suffix `_anchor.yaml` matches whether template is the
    canonical anchor for its `(grade, topic, family, difficulty)` cell.

    `anchor_ids_by_cell`: cell-key → the id of the anchor in that cell
    (or None if no anchor exists). Computed once by the corpus runner.
    """
    if template.file_path is None:
        return []
    has_suffix = template.file_path.name.endswith("_anchor.yaml")
    cell = (
        f"k{template.grade}", template.topic, template.family, template.difficulty,
    )
    canonical = anchor_ids_by_cell.get(cell)
    is_canonical = canonical == template.id

    out: List[Finding] = []
    if has_suffix and not is_canonical and canonical is not None:
        out.append(Finding(
            rule="anchor_filename_mismatch", severity="warning",
            template_id=template.id, file=_relpath(template.file_path),
            message=(
                f"filename ends with `_anchor.yaml` but cell already has anchor "
                f"'{canonical}'. Either rename, or pick exactly one canonical anchor."
            ),
        ))
    elif has_suffix and canonical is None:
        # Suffix declared anchor but loader didn't pick this template up
        # as anchor — should be impossible given the simple suffix check;
        # surface as a sanity warning anyway.
        out.append(Finding(
            rule="anchor_filename_mismatch", severity="warning",
            template_id=template.id, file=_relpath(template.file_path),
            message="filename ends with `_anchor.yaml` but cell has no anchor",
        ))
    return out


def check_off_anchor_divergence(
    template: TemplateDefinition,
    anchor_lookup: Dict[Tuple, TemplateDefinition],
) -> List[Finding]:
    """Variant whose variable set or step count diverges from its anchor.

    Cell key is `(grade, topic, family, difficulty)`. Variants in the
    same cell as their anchor should share the operation/step count and
    most of the variable spec — divergence usually means the variant
    has drifted into a structurally-different problem and should
    either become its own anchor or be culled.
    """
    if template.file_path is None or template.file_path.name.endswith("_anchor.yaml"):
        return []
    cell = (
        f"k{template.grade}", template.topic, template.family, template.difficulty,
    )
    anchor = anchor_lookup.get(cell)
    if anchor is None or anchor.id == template.id:
        return []

    findings: List[Finding] = []
    if template.steps != anchor.steps:
        findings.append(Finding(
            rule="off_anchor_divergence", severity="warning",
            template_id=template.id, file=_relpath(template.file_path),
            message=(
                f"steps={template.steps} diverges from anchor "
                f"'{anchor.id}' (steps={anchor.steps}). If the math shape "
                f"differs, this should be its own anchor."
            ),
            extra={
                "anchor_id": anchor.id, "anchor_steps": anchor.steps,
                "template_steps": template.steps,
            },
        ))

    var_diff = (
        set(template.variables.keys()) ^ set(anchor.variables.keys())
    )
    # Tolerate trivial naming additions (Answer1/Answer2 differences are
    # usually authorial polish). Flag only when ≥ 2 vars differ — the
    # signal we want is structural drift, not minor renames.
    if len(var_diff) >= 2:
        findings.append(Finding(
            rule="off_anchor_divergence", severity="warning",
            template_id=template.id, file=_relpath(template.file_path),
            message=(
                f"variable set diverges from anchor '{anchor.id}'. "
                f"Differing keys: {sorted(var_diff)}"
            ),
            extra={
                "anchor_id": anchor.id,
                "anchor_vars": sorted(anchor.variables.keys()),
                "template_vars": sorted(template.variables.keys()),
            },
        ))
    return findings


def check_fixture_missing(template: TemplateDefinition) -> List[Finding]:
    out: List[Finding] = []
    if not template.tests:
        out.append(Finding(
            rule="fixture_missing", severity="warning",
            template_id=template.id, file=_relpath(template.file_path),
            message="no test fixtures defined; add at least one for regression coverage",
        ))
        return out
    if template.difficulty_tiers:
        covered = {t.difficulty for t in template.tests if t.difficulty}
        missing = set(template.difficulty_tiers) - covered
        if missing:
            out.append(Finding(
                rule="fixture_missing", severity="warning",
                template_id=template.id, file=_relpath(template.file_path),
                message=(
                    f"multi-tier template missing fixture(s) for tier(s) "
                    f"{sorted(missing)}; tiers covered: {sorted(covered) or '[none]'}"
                ),
            ))
    return out


def check_visual_render(
    template: TemplateDefinition, renderer: JinjaRenderer, sample_context: Dict[str, Any],
) -> List[Finding]:
    """Smoke-render the visual block (TD-3.1c + Phase β H1).

    Format dispatch:
      - `svg`    : Jinja-render `visual.source` against the variable
                   context, parse the result as XML.
      - `python` : execute `visual.source` in the visual sandbox
                   (PlotSVG/TreeSVG/MarkovSVG); the captured `Visual`
                   binding must parse as XML.

    Either path emits `visual_render_crash` (error severity) on
    failure. `sample_context` is the rendered-context from a
    successful sample render so the visual sees the same variable
    values the problem text did.
    """
    if template.visual is None:
        return []
    rel = _relpath(template.file_path)

    if template.visual.format == "python":
        from ..solution_evaluator import build_visual_sandbox
        sandbox = build_visual_sandbox(language=template.language)
        # Same merged-namespace exec as template_generator._render_python_visual,
        # so lambdas inside visual.source close over context vars correctly.
        ns = {**sandbox, **sample_context}
        try:
            exec(template.visual.source, ns)
        except Exception as exc:
            return [Finding(
                rule="visual_render_crash", severity="error",
                template_id=template.id, file=rel,
                message=f"visual.source (python) raised: {type(exc).__name__}: {exc}",
            )]
        if "Visual" not in ns:
            return [Finding(
                rule="visual_render_crash", severity="error",
                template_id=template.id, file=rel,
                message="visual.source (python) did not bind `Visual`",
            )]
        rendered_source = ns["Visual"]
        if not isinstance(rendered_source, str):
            return [Finding(
                rule="visual_render_crash", severity="error",
                template_id=template.id, file=rel,
                message=(
                    f"visual.source (python) bound `Visual` to "
                    f"{type(rendered_source).__name__}, expected str"
                ),
            )]
    else:
        try:
            rendered_source = renderer.render(template.visual.source, sample_context)
        except Exception as exc:
            return [Finding(
                rule="visual_render_crash", severity="error",
                template_id=template.id, file=rel,
                message=f"visual.source Jinja render failed: {type(exc).__name__}: {exc}",
            )]

    try:
        ElementTree.fromstring(rendered_source.strip())
    except ElementTree.ParseError as exc:
        return [Finding(
            rule="visual_render_crash", severity="error",
            template_id=template.id, file=rel,
            message=f"visual.source rendered to invalid XML: {exc}",
        )]
    return []


def run_template_tests(template: TemplateDefinition) -> List[Finding]:
    """Run embedded test fixtures; flag drift.

    Mirrors the logic in `cli.test`: per fixture, render variables with
    the seed (and tier, for multi-tier), execute solution, format
    answer, compare with `expected.answer`. Differences emit
    `fixture_drifted` findings. Crashes emit `fixture_crashed`.
    """
    out: List[Finding] = []
    rel = _relpath(template.file_path)
    for i, test_case in enumerate(template.tests, 1):
        test_seed = test_case.seed
        expected = test_case.expected.get("answer", "")
        test_difficulty = test_case.difficulty or template.difficulty
        try:
            var_gen = VariableGenerator(seed=test_seed)
            context = var_gen.generate_context(
                template.variables, difficulty=test_difficulty,
            )
            answer_value = execute_solution(template.solution, context)
            if isinstance(answer_value, dict):
                parts = []
                for j in sorted(answer_value.keys()):
                    answer_spec = template.variables.get(f"Answer{j}")
                    parts.append(format_answer(answer_value[j], answer_spec))
                actual = " | ".join(parts)
            else:
                answer_spec = template.variables.get("Answer")
                actual = format_answer(answer_value, answer_spec)
        except Exception as exc:
            out.append(Finding(
                rule="fixture_crashed", severity="error",
                template_id=template.id, file=rel, seed=test_seed,
                message=f"fixture {i} (seed={test_seed}, tier={test_difficulty}) crashed: {exc}",
            ))
            continue

        if not compare_answers(
            actual, expected,
            mode=test_case.compare,
            tolerance=test_case.tolerance,
            tolerance_rel=test_case.tolerance_rel,
        ):
            out.append(Finding(
                rule="fixture_drifted", severity="error",
                template_id=template.id, file=rel, seed=test_seed,
                message=(
                    f"fixture {i} (seed={test_seed}, tier={test_difficulty}) drifted: "
                    f"expected {expected!r}, got {actual!r}"
                ),
                extra={"expected": expected, "actual": actual, "tier": test_difficulty},
            ))
    return out


# ---------------------------------------------------------------------------
# Per-template runner.
# ---------------------------------------------------------------------------

def lint_template(
    template: TemplateDefinition,
    template_generator: TemplateGenerator,
    samples_per_template: int = DEFAULT_SAMPLES,
    seed_base: int = DEFAULT_SEED_BASE,
    anchor_lookup: Optional[Dict[Tuple, TemplateDefinition]] = None,
    anchor_ids_by_cell: Optional[Dict[Tuple, str]] = None,
    rules: Optional[set[str]] = None,
) -> List[Finding]:
    """Run all enabled rules against one template.

    `anchor_lookup` and `anchor_ids_by_cell` are optional — when None,
    cross-template rules (`anchor_filename_mismatch`,
    `off_anchor_divergence`) are skipped. The corpus runner builds them
    once and threads them through.
    """
    findings: List[Finding] = []

    def enabled(rule: str) -> bool:
        return rules is None or rule in rules

    # Schema-derived
    if enabled("slug_noncanonical"):
        findings.extend(check_slug_canon(template))
    if enabled("zero_steps_with_ops") or enabled("very_high_step_count"):
        findings.extend(check_steps_ops_consistency(template))
    if enabled("track_missing"):
        findings.extend(check_track_missing(template))
    if enabled("noop_clauses_no_slot"):
        findings.extend(check_noop_clauses_no_slot(template))
    if enabled("simplification_lift_missing"):
        findings.extend(check_simplification_lift_missing(template))
    if enabled("feature_declared_but_unused"):
        findings.extend(check_feature_declared_but_unused(template))
    if enabled("fixture_missing"):
        findings.extend(check_fixture_missing(template))
    if enabled("anchor_filename_mismatch") and anchor_ids_by_cell is not None:
        findings.extend(check_anchor_filename_mismatch(template, anchor_ids_by_cell))
    if enabled("off_anchor_divergence") and anchor_lookup is not None:
        findings.extend(check_off_anchor_divergence(template, anchor_lookup))
    if enabled("fixture_drifted") or enabled("fixture_crashed"):
        findings.extend(run_template_tests(template))

    # Render-driven
    samples = render_samples(
        template, template_generator,
        samples_per_template=samples_per_template, seed_base=seed_base,
    )
    if not samples:
        findings.append(Finding(
            rule="render_crash", severity="error",
            template_id=template.id, file=_relpath(template.file_path),
            message=f"all {samples_per_template} render attempts crashed",
        ))
        return findings

    render_rules = [
        ("unrendered_jinja", check_unrendered_jinja),
        ("empty_answer", check_empty_answer),
        ("body_too_long", check_body_too_long),
        ("unit_spelled_cubic", check_units),
        ("unit_spelled_squared", check_units),
        ("gsm8k_money_change", check_gsm8k_saturation),
        ("gsm8k_with_tax", check_gsm8k_saturation),
        ("gsm8k_items_at_price_each", check_gsm8k_saturation),
        ("area_no_squared_unit", check_answer_units_match_topic),
        ("volume_no_cubed_unit", check_answer_units_match_topic),
        # γ.3 (A.4) — render-driven, prose ↔ schema consistency rules.
        ("figure_load_inconsistent", check_figure_load_inconsistent),
        ("visual_prose_contradiction", check_visual_prose_contradiction),
        # γ.4q (Q.3) — render-driven, rubric items 2 + 11.
        ("filler_boilerplate", check_filler_boilerplate),
        ("none_in_output", check_none_in_output),
    ]
    seen_render_fns: set = set()
    for s in samples:
        for rule_id, fn in render_rules:
            if not enabled(rule_id):
                continue
            # Multi-rule functions (check_units, check_gsm8k_saturation,
            # check_answer_units_match_topic) emit several rule ids each;
            # avoid running them more than once per sample.
            key = (id(fn), s.seed, s.tier)
            if key in seen_render_fns:
                continue
            seen_render_fns.add(key)
            findings.extend(fn(s, template))

    # Visual smoke uses the first successful sample's context — but the
    # context isn't returned by the generator API. Re-derive cheaply:
    needs_visual_render = (
        template.visual is not None
        and (
            enabled("visual_render_crash")
            or enabled("axis_range_artifact")
        )
    )
    if needs_visual_render:
        renderer = JinjaRenderer()
        # Use VariableGenerator directly to get a context dict, since
        # `_generate_from_template` returns the rendered output instead
        # of the context. Same seed as the first sample.
        vg = VariableGenerator(seed=samples[0].seed, locale=template.culture)
        ctx = vg.generate_context(
            template.variables,
            difficulty=samples[0].tier,
        )
        # Auto-injected `<var>_unit` companions matter for visuals too.
        for name, spec in template.variables.items():
            if spec.unit:
                ctx[f"{name}_unit"] = spec.unit
        ctx.setdefault("language", template.language)
        if enabled("visual_render_crash"):
            findings.extend(check_visual_render(template, renderer, ctx))
        if enabled("axis_range_artifact"):
            rendered_svg = _render_visual_silently(template, renderer, ctx)
            if rendered_svg:
                findings.extend(check_axis_range_artifact(rendered_svg, template))

    return findings


def _render_visual_silently(
    template: TemplateDefinition,
    renderer: JinjaRenderer,
    ctx: Dict[str, Any],
) -> Optional[str]:
    """Render the visual block and return the SVG string, or None on crash.

    Used by the γ.3 axis-artifact rule which only needs the rendered
    output — actual crash reporting goes through ``check_visual_render``.
    Mirrors that function's format dispatch (``svg`` Jinja-render vs
    ``python`` sandbox-exec).
    """
    if template.visual is None:
        return None
    try:
        if template.visual.format == "python":
            from ..solution_evaluator import build_visual_sandbox
            sandbox = build_visual_sandbox(language=template.language)
            ns = {**sandbox, **ctx}
            exec(template.visual.source, ns)
            value = ns.get("Visual")
            return value if isinstance(value, str) else None
        return renderer.render(template.visual.source, ctx)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Corpus runner.
# ---------------------------------------------------------------------------

def lint_corpus(
    templates_dir: Path,
    samples_per_template: int = DEFAULT_SAMPLES,
    seed_base: int = DEFAULT_SEED_BASE,
    rules: Optional[set[str]] = None,
) -> List[Finding]:
    """Lint every template under `templates_dir`.

    Returns a flat list of findings across all templates. Schema-load
    failures surface as `schema_invalid` findings (the loader prints
    its own errors to stderr too, like before).
    """
    templates = load_all_templates(templates_dir)
    return lint_loaded_templates(
        templates.values(), templates_dir,
        samples_per_template=samples_per_template,
        seed_base=seed_base, rules=rules,
    )


def lint_loaded_templates(
    templates,
    templates_dir: Path,
    samples_per_template: int = DEFAULT_SAMPLES,
    seed_base: int = DEFAULT_SEED_BASE,
    rules: Optional[set[str]] = None,
) -> List[Finding]:
    """Lint a list of pre-loaded templates. Used by the corpus runner
    and by the single-path runner that pre-loaded a directory.
    """
    templates = list(templates)
    template_generator = TemplateGenerator(templates_dir=templates_dir)

    anchor_lookup: Dict[Tuple, TemplateDefinition] = {}
    anchor_ids_by_cell: Dict[Tuple, str] = {}
    for tpl in templates:
        if tpl.file_path and tpl.file_path.name.endswith("_anchor.yaml"):
            cell = (f"k{tpl.grade}", tpl.topic, tpl.family, tpl.difficulty)
            anchor_lookup[cell] = tpl
            anchor_ids_by_cell[cell] = tpl.id

    findings: List[Finding] = []
    for tpl in templates:
        findings.extend(lint_template(
            tpl, template_generator,
            samples_per_template=samples_per_template,
            seed_base=seed_base,
            anchor_lookup=anchor_lookup,
            anchor_ids_by_cell=anchor_ids_by_cell,
            rules=rules,
        ))
    return findings


def lint_path(
    path: Path,
    samples_per_template: int = DEFAULT_SAMPLES,
    seed_base: int = DEFAULT_SEED_BASE,
    rules: Optional[set[str]] = None,
) -> List[Finding]:
    """Lint a single template file, a directory, or the default corpus.

    Single-file mode skips cross-template rules (off-anchor divergence,
    anchor filename mismatch) since the cell context isn't loaded.
    """
    if path.is_dir():
        return lint_corpus(
            path, samples_per_template=samples_per_template,
            seed_base=seed_base, rules=rules,
        )

    # Single file: load it standalone, but the TemplateGenerator still
    # needs a templates dir for the renderer environment. Use the
    # parent's parent (the topic dir's parent) so render-time imports
    # resolve.
    findings: List[Finding] = []
    template, load_findings = load_template_for_lint(path)
    findings.extend(load_findings)
    if template is None:
        return findings

    templates_dir = _project_templates_dir(path)
    template_generator = TemplateGenerator(templates_dir=templates_dir)

    findings.extend(lint_template(
        template, template_generator,
        samples_per_template=samples_per_template,
        seed_base=seed_base,
        rules=rules,
    ))
    return findings


# ---------------------------------------------------------------------------
# Helpers.
# ---------------------------------------------------------------------------

def _relpath(path: Optional[Path]) -> str:
    if path is None:
        return ""
    try:
        # cwd-relative is the friendliest output for both terminal humans
        # and CI logs.
        return str(path.resolve().relative_to(Path.cwd()))
    except Exception:
        return str(path)


def _project_templates_dir(path: Path) -> Path:
    """Walk up from a template file looking for `src/templates/`."""
    cur = path.resolve().parent
    for _ in range(8):
        candidate = cur / "src" / "templates"
        if candidate.is_dir():
            return candidate
        if cur.parent == cur:
            break
        cur = cur.parent
    # Fallback — use the path's own parent, which works for ad-hoc dirs.
    return path.resolve().parent
