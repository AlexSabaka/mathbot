"""γ.4r R.2 — Grader calibration suite.

Pins the full GradeFinding output that `grade_template` produces for
a fixed (template, samples, model raw responses) tuple. If the grader
changes anything about how it emits findings — rule names, severity
mapping, note formatting, R.1-style overrides — these tests fire and
the diff shows what changed.

Two layers:

- **R.2a snapshots** (`TestCalibrationSnapshots`) — three pinned
  scenarios spanning the failure-class space:
    * clean addition (all model verdicts pass except visual-related)
    * subtraction with a negative-answer model verdict
    * K1.4 word-count hallucination (model lies, R.1a overrides)
  Each scenario mocks `urlopen` and `render_samples`, calls
  `grade_template`, and asserts the resulting findings equal a
  pinned dict-of-tuples. Visual-related items (K1.1, K1.2, K1.3,
  agnostic.12) are model-driven — their fail verdicts on K1
  templates without `visual:` blocks are real signal, not noise.

- **R.2b noise smoke test** (`TestGraderNoiseStability`) —
  optionally runs against a live Ollama instance. Tagged
  `@pytest.mark.requires_ollama`; skipped by default. Calls
  `grade_template` 10 times against a clean K1 template and
  asserts ≥ 80% verdict stability per item (the same item fires
  with the same pass/fail across most seeds). Catches prompt-format
  regressions and model swaps that quietly destabilize the rubric.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from src.audit.render import RenderedSample
from src.grading.grader import grade_template
from src.grading.rubrics import items_for
from src.template_generator import TemplateGenerator
from src.yaml_loader import YAMLLoader


REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = REPO_ROOT / "src" / "templates"


# ---------------------------------------------------------------------------
# Fake urlopen / response wiring (parallels tests/test_grading.py).
# ---------------------------------------------------------------------------

class _FakeResp:
    def __init__(self, body: bytes):
        self._body = body

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


def _envelope(items_payload: list) -> bytes:
    """Return a serialized Ollama envelope for the given verdict list."""
    inner = json.dumps({"items": items_payload})
    return json.dumps({"response": inner}).encode("utf-8")


# ---------------------------------------------------------------------------
# Snapshot scenarios — full GradeFinding shape pinned.
# ---------------------------------------------------------------------------

class TestCalibrationSnapshots:
    """Pinned full-output regression tests. If the grader's emission
    behavior changes, the asserted dict diff makes the change explicit."""

    def _grader_inputs(self, template_path: Path, body: str, answer: str):
        loader = YAMLLoader()
        template = loader.load_template(template_path)
        gen = TemplateGenerator(templates_dir=TEMPLATES_DIR)
        sample = RenderedSample(
            template_id=template.id, seed=0, tier="easy",
            body=body, answer=answer, raw={},
        )
        return template, gen, sample

    def _findings_to_pinned(self, findings):
        """Reduce findings to a stable comparable shape: list of
        (rule, severity, pass, note) tuples in emission order."""
        return [
            (f.rule, f.severity, f.extra["pass"], f.extra["note"])
            for f in findings
        ]

    def test_clean_addition_full_snapshot(self):
        """Clean K1 addition rendered without a visual block. Model
        fires K1.1 / K1.2 / K1.3 / agnostic.12 as fail with "no image
        attached" notes — these are real signal on a K1 corpus that
        ought to be picture-anchored, not noise. R.1c strips the
        redundant 'No image attached;' prefix from each note."""
        template_path = TEMPLATES_DIR / "arithmetic" / "k1_easy_addition_01_anchor.yaml"
        if not template_path.exists():
            pytest.skip("fixture template missing")
        template, gen, sample = self._grader_inputs(
            template_path, body="3 + 5 = ?", answer="8",
        )
        items = items_for("all", with_image=True)
        # Mirror the actual K1-sweep model behavior: visual-related
        # items (K1.1, K1.2, K1.3, agnostic.12) fire fail with a
        # 'No image attached; …' note. Everything else passes.
        visual_items = {"k1.1", "k1.2", "k1.3", "agnostic.12"}

        def fake_urlopen(req, timeout=None):
            payload = []
            for it in items:
                if it.id in visual_items:
                    payload.append({
                        "id": it.id, "pass": False,
                        "note": f"No image attached; {it.name} fails.",
                    })
                else:
                    payload.append({"id": it.id, "pass": True, "note": ""})
            return _FakeResp(_envelope(payload))

        with patch("urllib.request.urlopen", side_effect=fake_urlopen), \
             patch("src.grading.grader.render_samples", return_value=[sample]):
            findings = grade_template(
                template, gen,
                samples_per_template=1,
                rubric_set="all",
                with_image=True,
            )

        actual = self._findings_to_pinned(findings)
        # Pinned expected output. Rule order is items_for("all",
        # with_image=True): 12 agnostic + 8 k1 = 20 findings.
        # R.1c strips "No image attached; " from every visual-item note.
        expected = [
            ("grading.agnostic.1", "info", True, ""),
            ("grading.agnostic.2", "info", True, ""),
            ("grading.agnostic.3", "info", True, ""),
            ("grading.agnostic.4", "info", True, ""),
            ("grading.agnostic.5", "info", True, ""),
            ("grading.agnostic.6", "info", True, ""),
            ("grading.agnostic.7", "info", True, ""),
            ("grading.agnostic.8", "info", True, ""),
            ("grading.agnostic.9", "info", True, ""),
            ("grading.agnostic.10", "info", True, ""),
            ("grading.agnostic.11", "info", True, ""),
            (
                "grading.agnostic.12", "error", False,
                "Visual integrity (if visual block present) fails.",
            ),
            ("grading.k1.1", "error", False, "Visual block present fails."),
            (
                "grading.k1.2", "error", False,
                "Visual is load-bearing or prose is sufficient fails.",
            ),
            ("grading.k1.3", "error", False, "Visual matches prose fails."),
            ("grading.k1.4", "info", True, ""),
            ("grading.k1.5", "info", True, ""),
            ("grading.k1.6", "info", True, ""),
            ("grading.k1.7", "info", True, ""),
            ("grading.k1.8", "info", True, ""),
        ]
        assert actual == expected

    def test_subtraction_with_negative_answer_full_snapshot(self):
        """A subtraction template that produces a negative answer at
        some seed (the scenario γ.4r R.3a's pre-fix
        `k1_easy_subtraction_01` exhibited). The model emits the
        agnostic.3 / k1.7 / k1.8 fails the K1 grading sweep
        actually saw in `output_grading_k1/`."""
        template_path = TEMPLATES_DIR / "arithmetic" / "k1_easy_subtraction_01_anchor.yaml"
        if not template_path.exists():
            pytest.skip("fixture template missing")
        # Use a simulated body — even if R.3a fixed the bounds, this
        # snapshot is about how the grader REACTS to a negative
        # answer, regardless of whether the template can produce one.
        template, gen, sample = self._grader_inputs(
            template_path, body="2 - 5 = ?", answer="-3",
        )
        items = items_for("all", with_image=True)

        # Model verdicts mirroring the actual reports under
        # output_grading_k1/k1_easy_subtraction_01_anchor.json seed=1.
        # Visual-related items also fail because the K1 template has
        # no visual block (real signal, not noise).
        fail_set = {
            "agnostic.3": "Answer -3 is negative; K1 range requires 0-20 whole numbers.",
            "agnostic.12": "No image attached; visual integrity unverifiable.",
            "k1.1": "No image present; K1 problems require visual block.",
            "k1.2": "No image present; figure is load-bearing for K1.",
            "k1.3": "No image attached; visual quantity cannot be verified.",
            "k1.7": "Answer -3 is outside K1 numeral range 0-20.",
            "k1.8": "Answer -3 is not a small whole number suitable for K1.",
        }

        def fake_urlopen(req, timeout=None):
            payload = []
            for it in items:
                if it.id in fail_set:
                    payload.append({
                        "id": it.id, "pass": False, "note": fail_set[it.id],
                    })
                else:
                    payload.append({"id": it.id, "pass": True, "note": ""})
            return _FakeResp(_envelope(payload))

        with patch("urllib.request.urlopen", side_effect=fake_urlopen), \
             patch("src.grading.grader.render_samples", return_value=[sample]):
            findings = grade_template(
                template, gen,
                samples_per_template=1,
                rubric_set="all",
                with_image=True,
            )

        # Pin only the substantive aspects: severity by rule + note text
        # for failing findings. Pass-findings have no note variation
        # worth pinning.
        sev_by_rule = {f.rule: f.severity for f in findings}
        notes_by_rule = {
            f.rule: f.extra["note"] for f in findings if f.severity == "error"
        }
        assert sev_by_rule == {
            "grading.agnostic.1": "info",
            "grading.agnostic.2": "info",
            "grading.agnostic.3": "error",
            "grading.agnostic.4": "info",
            "grading.agnostic.5": "info",
            "grading.agnostic.6": "info",
            "grading.agnostic.7": "info",
            "grading.agnostic.8": "info",
            "grading.agnostic.9": "info",
            "grading.agnostic.10": "info",
            "grading.agnostic.11": "info",
            "grading.agnostic.12": "error",
            "grading.k1.1": "error",
            "grading.k1.2": "error",
            "grading.k1.3": "error",
            "grading.k1.4": "info",
            "grading.k1.5": "info",
            "grading.k1.6": "info",
            "grading.k1.7": "error",
            "grading.k1.8": "error",
        }
        # R.1c strips "No image attached; " / "No image present; " from
        # the visual-related notes.
        assert notes_by_rule == {
            "grading.agnostic.3": "Answer -3 is negative; K1 range requires 0-20 whole numbers.",
            "grading.agnostic.12": "visual integrity unverifiable.",
            "grading.k1.1": "K1 problems require visual block.",
            "grading.k1.2": "figure is load-bearing for K1.",
            "grading.k1.3": "visual quantity cannot be verified.",
            "grading.k1.7": "Answer -3 is outside K1 numeral range 0-20.",
            "grading.k1.8": "Answer -3 is not a small whole number suitable for K1.",
        }

    def test_k14_hallucination_overridden(self):
        """The dominant grader-noise mode in the K1 sweep:
        `output_grading_k1/k1_medium_addition_02.json` has
        K1.4 = "Prose is 23 words, exceeding 25-word limit" — a
        confident fail on a body that's literally under the limit.
        R.1a overrides with the deterministic count."""
        template_path = TEMPLATES_DIR / "arithmetic" / "k1_easy_addition_01_anchor.yaml"
        if not template_path.exists():
            pytest.skip("fixture template missing")
        # A body that's 4 words long. No way it exceeds 25.
        template, gen, sample = self._grader_inputs(
            template_path, body="Tom has 5 apples.", answer="5",
        )
        items = items_for("k1", with_image=True)

        def fake_urlopen(req, timeout=None):
            payload = []
            for it in items:
                if it.id == "k1.4":
                    payload.append({
                        "id": "k1.4", "pass": False,
                        "note": "Prose is 23 words, exceeding 25-word limit",
                    })
                elif it.id in {"k1.1", "k1.2", "k1.3"}:
                    payload.append({
                        "id": it.id, "pass": False,
                        "note": "No image attached.",
                    })
                else:
                    payload.append({"id": it.id, "pass": True, "note": ""})
            return _FakeResp(_envelope(payload))

        with patch("urllib.request.urlopen", side_effect=fake_urlopen), \
             patch("src.grading.grader.render_samples", return_value=[sample]):
            findings = grade_template(
                template, gen,
                samples_per_template=1,
                rubric_set="k1",
                with_image=True,
            )

        k14 = [f for f in findings if f.rule == "grading.k1.4"]
        assert len(k14) == 1
        # R.1a override: model said fail; deterministic count says pass
        # (4 words ≤ 25), so the override emits info-severity.
        assert k14[0].severity == "info"
        assert k14[0].extra["pass"] is True
        assert k14[0].extra["note"] == ""


# ---------------------------------------------------------------------------
# R.2b — Live-Ollama noise smoke test.
# ---------------------------------------------------------------------------

class TestGraderNoiseStability:
    """Verdict-stability smoke test against a live Ollama instance.
    Skipped by default; opt in with `MATHBOT_GRADER_LIVE=1` and a
    running ollama daemon at the default host. Bumps a clean K1
    template through 10 seeds and asserts ≥ 80% per-item verdict
    stability — the same rubric item should land on the same pass/fail
    verdict at most seeds. Catches prompt-format regressions and
    model swaps that quietly destabilize the rubric."""

    @pytest.mark.skipif(
        not os.environ.get("MATHBOT_GRADER_LIVE"),
        reason="set MATHBOT_GRADER_LIVE=1 to run against live ollama",
    )
    def test_clean_addition_at_10_seeds(self):
        from collections import defaultdict

        loader = YAMLLoader()
        template_path = TEMPLATES_DIR / "arithmetic" / "k1_easy_addition_01_anchor.yaml"
        if not template_path.exists():
            pytest.skip("fixture template missing")
        template = loader.load_template(template_path)
        gen = TemplateGenerator(templates_dir=TEMPLATES_DIR)

        per_item: dict = defaultdict(list)
        N = 10
        for seed_base in range(N):
            findings = grade_template(
                template, gen,
                samples_per_template=1,
                seed_base=seed_base,
                rubric_set="all",
                with_image=True,
                model=os.environ.get("MATHBOT_GRADER_MODEL", "qwen3.5:9b"),
            )
            for f in findings:
                if f.rule.startswith("grading.") and not f.rule.endswith(
                    "parse_error",
                ):
                    per_item[f.rule].append(f.extra["pass"])

        assert per_item, "no item findings collected — grader returned nothing"

        # Per-item stability: max(majority-vote frequency) / N ≥ 0.8.
        unstable = []
        for rule, verdicts in per_item.items():
            if len(verdicts) < N:
                continue  # parse errors at some seeds — skip
            true_n = sum(1 for v in verdicts if v)
            stability = max(true_n, N - true_n) / N
            if stability < 0.8:
                unstable.append((rule, true_n, N))
        assert not unstable, (
            f"unstable items (less than 80% verdict stability across {N} "
            f"seeds): {unstable}"
        )
