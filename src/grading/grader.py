"""Per-template and corpus-level grading orchestration.

Mirrors `src.audit.lint.lint_template` / `lint_corpus` in shape: render
K samples once via `src.audit.render.render_samples`, then run each
sample past the rubric. The Ollama call lives behind
`src.grading.ollama.call_ollama` so this module stays focused on prompt
construction and verdict-to-finding mapping.
"""

from __future__ import annotations

import base64
import json
import sys
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from ..audit.render import RenderedSample, render_samples
from ..template_generator import TemplateGenerator
from ..yaml_loader import TemplateDefinition, load_all_templates
from .findings import GradeFinding
from .ollama import DEFAULT_HOST, OllamaError, call_ollama
from .rubrics import RubricItem, items_for


DEFAULT_MODEL = "qwen3.5:2b"
DEFAULT_SAMPLES = 2          # LLM calls are slow — fewer than lint's 4.
DEFAULT_SEED_BASE = 0

# K1.4 prose-length grader override threshold. The rubric phrases this
# as "≤ ~25 words"; we use a hard 25 cutoff for determinism.
_K1_PROSE_WORD_LIMIT = 25

# Note prefixes the grader strips from model output. The model leads
# many notes with a "no image attached" preamble that is redundant
# once R.1b filters the no-image-dependent items out of the prompt.
_NO_IMAGE_NOTE_PREFIXES = (
    "No image attached;",
    "No image attached.",
    "No image attached,",
    "No image present;",
    "No image present.",
    "No image present,",
    "No image attached",
    "No image present",
)


# ---------------------------------------------------------------------------
# Prompt construction.
# ---------------------------------------------------------------------------

def build_prompt(
    template: TemplateDefinition,
    sample: RenderedSample,
    items: List[RubricItem],
    *,
    image_attached: bool,
) -> str:
    """Build the user-turn prompt sent to Ollama for one render.

    The shape (numbered rubric, explicit output skeleton with every id
    pre-filled) is tuned for small models — qwen3.5:2b otherwise emits
    `{"items": []}` because the rubric block alone doesn't communicate
    that all ids are mandatory.
    """
    rubric_lines: List[str] = []
    for n, it in enumerate(items, start=1):
        rubric_lines.append(f'{n}. [id="{it.id}"] {it.prompt}')
    rubric_block = "\n".join(rubric_lines)

    image_note = (
        "An image of the rendered figure is attached."
        if image_attached
        else "No image is attached. For criteria that require the figure, "
             "answer pass=true with note=\"no image\"."
    )

    # Pre-built skeleton showing one verdict per id — this is the most
    # reliable nudge for small models to emit the full set rather than
    # an empty array.
    skeleton_entries = ",\n    ".join(
        f'{{"id": "{it.id}", "pass": true, "note": ""}}' for it in items
    )
    skeleton = '{\n  "items": [\n    ' + skeleton_entries + '\n  ]\n}'

    return (
        "You grade a math problem template against a binary rubric.\n"
        f"{image_note}\n\n"
        f"Apply each of the {len(items)} rubric items below. For each item, "
        "decide pass (true) or fail (false). When fail, write a short note "
        "(≤15 words). When pass, leave note empty.\n\n"
        "Rubric:\n"
        f"{rubric_block}\n\n"
        "Rendered prose:\n"
        "---\n"
        f"{sample.body}\n"
        "---\n\n"
        "Fixture answer:\n"
        f"{sample.answer}\n\n"
        f"Topic: {template.topic}   Family: {template.family}   "
        f"Grade: k{template.grade}\n\n"
        "Output exactly one JSON object with this shape, with all "
        f"{len(items)} ids present, in this order. Replace pass/note for each "
        "item based on the rubric. No prose, no markdown, no extra keys, no "
        "missing ids:\n\n"
        f"{skeleton}\n"
    )


# ---------------------------------------------------------------------------
# SVG → PNG (in-memory). cairosvg is an optional `[png]` extra; missing
# it is recoverable — the grader falls back to text-only.
# ---------------------------------------------------------------------------

def svg_to_png_b64(svg_source: str, *, dpi: int = 150) -> Optional[str]:
    """Rasterize SVG markup to base64 PNG. Returns None if cairosvg missing
    or the rasterizer raised (malformed SVG, etc.) — the caller treats
    None as "no image to attach"."""
    try:
        import cairosvg  # type: ignore
    except ImportError:
        return None
    try:
        buf = BytesIO()
        cairosvg.svg2png(
            bytestring=svg_source.encode("utf-8"),
            write_to=buf,
            dpi=dpi,
        )
    except Exception:
        return None
    return base64.b64encode(buf.getvalue()).decode("ascii")


# ---------------------------------------------------------------------------
# Verdict parsing.
# ---------------------------------------------------------------------------

def _parse_verdicts(
    raw_response_text: str,
    expected_ids: List[str],
) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    """Parse Ollama's response text into a list of `{id, pass, note}` dicts.

    Returns `(verdicts, None)` on success or `(None, error_message)` if
    the response can't be coerced into the expected shape. Tolerates
    leading/trailing whitespace and code-fences but not free prose.
    """
    text = raw_response_text.strip()
    # Strip a single ```json ... ``` fence if the model added one
    # despite being told not to.
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
        text = text.strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        return None, f"json decode failed: {exc}"
    if not isinstance(data, dict) or "items" not in data:
        return None, "response missing 'items' key"
    items = data["items"]
    if not isinstance(items, list):
        return None, "'items' is not a list"

    seen: Dict[str, Dict[str, Any]] = {}
    for entry in items:
        if not isinstance(entry, dict):
            return None, "'items' entry is not an object"
        item_id = entry.get("id")
        if not isinstance(item_id, str):
            return None, "verdict missing string 'id'"
        if "pass" not in entry:
            return None, f"verdict for {item_id!r} missing 'pass'"
        seen[item_id] = entry

    missing = [i for i in expected_ids if i not in seen]
    if missing:
        return None, f"missing verdicts for: {', '.join(missing)}"

    return [seen[i] for i in expected_ids], None


# ---------------------------------------------------------------------------
# Per-template grader.
# ---------------------------------------------------------------------------

def grade_template(
    template: TemplateDefinition,
    template_generator: TemplateGenerator,
    *,
    model: str = DEFAULT_MODEL,
    samples_per_template: int = DEFAULT_SAMPLES,
    seed_base: int = DEFAULT_SEED_BASE,
    rubric_set: str = "all",
    with_image: bool = True,
    ollama_host: str = DEFAULT_HOST,
) -> List[GradeFinding]:
    """Grade one template against the rubric across K seeds.

    Skips K1-specific items when grade != 1. If the rubric set is
    `agnostic`, K1 items aren't requested anyway and any grade is
    acceptable.
    """
    # K1 items only make sense for grade == 1.
    effective_set = rubric_set
    if rubric_set in ("k1", "all") and template.grade != 1:
        if rubric_set == "k1":
            return [GradeFinding(
                rule="grading.skipped",
                severity="info",
                template_id=template.id,
                file=_relpath(template.file_path),
                message=f"k1 rubric not applicable (grade={template.grade})",
            )]
        effective_set = "agnostic"

    items = items_for(effective_set, with_image=with_image)
    expected_ids = [it.id for it in items]

    samples = render_samples(
        template, template_generator,
        samples_per_template=samples_per_template,
        seed_base=seed_base,
    )
    if not samples:
        return [GradeFinding(
            rule="grading.render_crash",
            severity="error",
            template_id=template.id,
            file=_relpath(template.file_path),
            message=f"all {samples_per_template} render attempts crashed",
        )]

    findings: List[GradeFinding] = []
    rel = _relpath(template.file_path)

    for sample in samples:
        image_b64 = None
        if with_image:
            visual = sample.raw.get("visual") or {}
            svg_source = visual.get("source")
            if isinstance(svg_source, str) and svg_source.strip():
                b64 = svg_to_png_b64(svg_source)
                if b64:
                    image_b64 = [b64]
        prompt = build_prompt(
            template, sample, items, image_attached=image_b64 is not None,
        )

        verdicts, err, raw = _call_and_parse(
            model=model,
            prompt=prompt,
            image_b64=image_b64,
            expected_ids=expected_ids,
            ollama_host=ollama_host,
        )

        if verdicts is None:
            extra: Dict[str, Any] = {"model": model, "tier": sample.tier}
            if raw:
                extra["raw"] = raw[:2000]
            findings.append(GradeFinding(
                rule="grading.parse_error",
                severity="error",
                template_id=template.id,
                file=rel,
                seed=sample.seed,
                message=err or "unknown parse failure",
                extra=extra,
            ))
            continue

        for verdict, item in zip(verdicts, items):
            # R.1a: K1.4 prose-length is decided client-side by actual
            # word count of the rendered body, overriding any model
            # hallucination ("Prose is 16 words, exceeding 25-word limit"
            # — fired multiple times in the original K1 sweep).
            if item.id == "k1.4":
                actual_words = len(sample.body.split())
                if actual_words > _K1_PROSE_WORD_LIMIT:
                    verdict = {
                        "id": "k1.4", "pass": False,
                        "note": (
                            f"Prose is {actual_words} words, exceeding "
                            f"{_K1_PROSE_WORD_LIMIT}-word limit"
                        ),
                    }
                else:
                    verdict = {"id": "k1.4", "pass": True, "note": ""}

            passed = bool(verdict.get("pass"))
            # R.1c: strip the redundant "No image attached;" / "No image
            # present;" preamble the model leads many notes with —
            # cosmetic; substantive text after the preamble is preserved.
            note = _strip_no_image_prefix(str(verdict.get("note") or ""))
            findings.append(GradeFinding(
                rule=f"grading.{item.id}",
                severity="info" if passed else "error",
                template_id=template.id,
                file=rel,
                seed=sample.seed,
                message=("pass" if passed else (note or item.name)),
                extra={
                    "item_name": item.name,
                    "model": model,
                    "tier": sample.tier,
                    "pass": passed,
                    "note": note,
                },
            ))

    return findings


def _strip_no_image_prefix(note: str) -> str:
    """Strip a leading 'No image attached;' / 'No image present;' from
    a note. The model emits this preamble even on items that have
    nothing to do with the image; once R.1b filters out the
    image-dependent rubric items, the preamble is pure noise."""
    s = note.strip()
    for prefix in _NO_IMAGE_NOTE_PREFIXES:
        if s.startswith(prefix):
            s = s[len(prefix):].strip()
            break
    return s


def _call_and_parse(
    *,
    model: str,
    prompt: str,
    image_b64: Optional[List[str]],
    expected_ids: List[str],
    ollama_host: str,
) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str], Optional[str]]:
    """Call Ollama once at temperature 0; on schema/parse fail, retry
    once at temperature 0.1.

    Returns `(verdicts, error_message, last_raw_text)`. The raw text from
    the final attempt is surfaced so the parse-error finding can include
    it in `extra.raw` for debugging.
    """
    last_raw: Optional[str] = None
    for attempt, temperature in enumerate((0.0, 0.1)):
        try:
            response = call_ollama(
                model=model,
                prompt=prompt,
                image_b64=image_b64,
                host=ollama_host,
                temperature=temperature,
            )
        except OllamaError as exc:
            if attempt == 1:
                return None, f"ollama error: {exc}", last_raw
            continue
        raw_text = response.get("response", "")
        # Reasoning models (qwen3.5:*) sometimes leak their answer into
        # the `thinking` channel even with `think: false`. Fall back to
        # it when `response` is empty so we don't waste a retry.
        if isinstance(raw_text, str) and not raw_text.strip():
            thinking = response.get("thinking")
            if isinstance(thinking, str) and thinking.strip():
                raw_text = thinking
        if not isinstance(raw_text, str):
            if attempt == 1:
                return None, "ollama response field is not a string", last_raw
            continue
        last_raw = raw_text
        verdicts, err = _parse_verdicts(raw_text, expected_ids)
        if verdicts is not None:
            return verdicts, None, raw_text
        if attempt == 1:
            return None, err, raw_text
    return None, "exhausted retries", last_raw


# ---------------------------------------------------------------------------
# Corpus / path runners.
# ---------------------------------------------------------------------------

def grade_corpus(
    templates_dir: Path,
    *,
    model: str = DEFAULT_MODEL,
    samples_per_template: int = DEFAULT_SAMPLES,
    seed_base: int = DEFAULT_SEED_BASE,
    rubric_set: str = "all",
    with_image: bool = True,
    ollama_host: str = DEFAULT_HOST,
    grade_filter: Optional[int] = 1,
    progress: bool = False,
) -> List[GradeFinding]:
    """Grade every (matching) template under `templates_dir`.

    `grade_filter` defaults to 1 because v1 is K1-only. Pass None to
    grade every template the rubric set covers.
    """
    templates = load_all_templates(templates_dir)
    return grade_loaded_templates(
        templates.values(), templates_dir,
        model=model,
        samples_per_template=samples_per_template,
        seed_base=seed_base,
        rubric_set=rubric_set,
        with_image=with_image,
        ollama_host=ollama_host,
        grade_filter=grade_filter,
        progress=progress,
    )


def grade_loaded_templates(
    templates: Iterable[TemplateDefinition],
    templates_dir: Path,
    *,
    model: str = DEFAULT_MODEL,
    samples_per_template: int = DEFAULT_SAMPLES,
    seed_base: int = DEFAULT_SEED_BASE,
    rubric_set: str = "all",
    with_image: bool = True,
    ollama_host: str = DEFAULT_HOST,
    grade_filter: Optional[int] = 1,
    progress: bool = False,
) -> List[GradeFinding]:
    """Grade a pre-loaded list of templates against the rubric."""
    templates = [
        t for t in templates
        if grade_filter is None or t.grade == grade_filter
    ]
    template_generator = TemplateGenerator(templates_dir=templates_dir)

    findings: List[GradeFinding] = []
    total = len(templates)
    for i, tpl in enumerate(templates, start=1):
        if progress:
            print(
                f"  grading [{i}/{total}] {tpl.id} ...",
                file=sys.stderr, flush=True,
            )
        findings.extend(grade_template(
            tpl, template_generator,
            model=model,
            samples_per_template=samples_per_template,
            seed_base=seed_base,
            rubric_set=rubric_set,
            with_image=with_image,
            ollama_host=ollama_host,
        ))
    return findings


def grade_path(
    path: Path,
    *,
    model: str = DEFAULT_MODEL,
    samples_per_template: int = DEFAULT_SAMPLES,
    seed_base: int = DEFAULT_SEED_BASE,
    rubric_set: str = "all",
    with_image: bool = True,
    ollama_host: str = DEFAULT_HOST,
    grade_filter: Optional[int] = 1,
    progress: bool = False,
) -> List[GradeFinding]:
    """Grade a single file or a directory. Mirrors `lint_path`."""
    if path.is_dir():
        return grade_corpus(
            path,
            model=model,
            samples_per_template=samples_per_template,
            seed_base=seed_base,
            rubric_set=rubric_set,
            with_image=with_image,
            ollama_host=ollama_host,
            grade_filter=grade_filter,
            progress=progress,
        )

    # Single-file: load standalone, but keep the templates_dir for the
    # renderer environment by walking up to src/templates/.
    from ..audit.lint import (
        _project_templates_dir,
        load_template_for_lint,
    )
    template, load_findings = load_template_for_lint(path)
    findings: List[GradeFinding] = [
        GradeFinding(
            rule=f.rule, severity=f.severity, template_id=f.template_id,
            file=f.file, message=f.message, seed=f.seed, extra=dict(f.extra),
        )
        for f in load_findings
    ]
    if template is None:
        return findings
    if grade_filter is not None and template.grade != grade_filter:
        return findings  # silently skip — caller picked the wrong file

    templates_dir = _project_templates_dir(path)
    template_generator = TemplateGenerator(templates_dir=templates_dir)
    findings.extend(grade_template(
        template, template_generator,
        model=model,
        samples_per_template=samples_per_template,
        seed_base=seed_base,
        rubric_set=rubric_set,
        with_image=with_image,
        ollama_host=ollama_host,
    ))
    return findings


def _relpath(path: Optional[Path]) -> str:
    if path is None:
        return ""
    try:
        return str(path.resolve().relative_to(Path.cwd()))
    except Exception:
        return str(path)
