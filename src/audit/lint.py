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
from ..solution_evaluator import execute_solution, format_answer
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
    """Smoke-render the visual block (TD-3.1c).

    Catches broken Jinja (undefined var) and malformed XML in
    `visual.source`. `sample_context` is the rendered-context from a
    successful sample render — reuses the variable values already
    generated, so the visual gets the same vars the problem text saw.
    """
    if template.visual is None:
        return []
    rel = _relpath(template.file_path)
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

        if actual != expected:
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
    if enabled("visual_render_crash") and template.visual is not None:
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
        findings.extend(check_visual_render(template, renderer, ctx))

    return findings


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
