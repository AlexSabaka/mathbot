"""Tests for `src.grading` — runs without a live Ollama by patching
`urllib.request.urlopen`.
"""

import json
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import pytest

from src.grading.findings import GradeFinding
from src.grading.grader import (
    _parse_verdicts,
    build_prompt,
    grade_path,
    grade_template,
)
from src.grading.rubrics import (
    AGNOSTIC_ITEMS,
    K1_ITEMS,
    items_for,
)
from src.audit.render import RenderedSample
from src.template_generator import TemplateGenerator
from src.yaml_loader import YAMLLoader


REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = REPO_ROOT / "src" / "templates"
K1_SAMPLE = TEMPLATES_DIR / "numbers" / "k1_easy_counting_02.yaml"


# ---------------------------------------------------------------------------
# Helpers — build a fake urlopen response.
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


def _ollama_response(items_payload):
    """Wrap an items list in the Ollama envelope and return raw bytes."""
    inner = json.dumps({"items": items_payload})
    envelope = json.dumps({"response": inner})
    return _FakeResp(envelope.encode("utf-8"))


# ---------------------------------------------------------------------------
# Rubric metadata.
# ---------------------------------------------------------------------------

class TestRubrics:
    def test_counts(self):
        assert len(AGNOSTIC_ITEMS) == 12
        assert len(K1_ITEMS) == 8

    def test_image_filter_drops_visual_items(self):
        all_items = items_for("all", with_image=True)
        text_only = items_for("all", with_image=False)
        dropped = {i.id for i in all_items} - {i.id for i in text_only}
        # K1.1, K1.3, agnostic.12 require an image.
        assert dropped == {"k1.1", "k1.3", "agnostic.12"}

    def test_unknown_set_raises(self):
        with pytest.raises(ValueError):
            items_for("k7", with_image=True)


# ---------------------------------------------------------------------------
# Prompt builder — snapshot-style, no Ollama call.
# ---------------------------------------------------------------------------

class TestPromptBuilder:
    def test_includes_all_item_ids(self):
        loader = YAMLLoader()
        template = loader.load_template(K1_SAMPLE)
        sample = RenderedSample(
            template_id=template.id, seed=42, tier="easy",
            body="Tom has 5 apples. How many apples does Tom have?",
            answer="5",
            raw={},
        )
        items = items_for("all", with_image=False)
        prompt = build_prompt(template, sample, items, image_attached=False)

        for item in items:
            assert item.id in prompt
        # Sanity: the rendered prose and answer appear verbatim.
        assert "5 apples" in prompt
        assert "Fixture answer:" in prompt
        # The image-attached note flips with the flag.
        assert "No image is attached" in prompt

    def test_image_attached_flag_changes_prompt(self):
        loader = YAMLLoader()
        template = loader.load_template(K1_SAMPLE)
        sample = RenderedSample(
            template_id=template.id, seed=0, tier="easy",
            body="x", answer="y", raw={},
        )
        items = items_for("k1", with_image=True)
        prompt = build_prompt(template, sample, items, image_attached=True)
        assert "image of the rendered figure is attached" in prompt


# ---------------------------------------------------------------------------
# Verdict parser.
# ---------------------------------------------------------------------------

class TestParseVerdicts:
    def test_clean_response(self):
        verdicts, err = _parse_verdicts(
            json.dumps({"items": [
                {"id": "agnostic.1", "pass": True, "note": ""},
                {"id": "agnostic.2", "pass": False, "note": "filler"},
            ]}),
            expected_ids=["agnostic.1", "agnostic.2"],
        )
        assert err is None
        assert verdicts is not None
        assert verdicts[0]["pass"] is True
        assert verdicts[1]["note"] == "filler"

    def test_strips_code_fence(self):
        text = "```json\n" + json.dumps({"items": [
            {"id": "agnostic.1", "pass": True, "note": ""},
        ]}) + "\n```"
        verdicts, err = _parse_verdicts(text, expected_ids=["agnostic.1"])
        assert err is None
        assert verdicts is not None

    def test_missing_id_fails(self):
        verdicts, err = _parse_verdicts(
            json.dumps({"items": [
                {"id": "agnostic.1", "pass": True, "note": ""},
            ]}),
            expected_ids=["agnostic.1", "agnostic.2"],
        )
        assert verdicts is None
        assert "missing verdicts" in err

    def test_garbage_response(self):
        verdicts, err = _parse_verdicts(
            "not json at all",
            expected_ids=["agnostic.1"],
        )
        assert verdicts is None
        assert "json decode failed" in err

    def test_orders_verdicts_by_expected_ids(self):
        verdicts, err = _parse_verdicts(
            json.dumps({"items": [
                {"id": "agnostic.2", "pass": False, "note": "x"},
                {"id": "agnostic.1", "pass": True, "note": ""},
            ]}),
            expected_ids=["agnostic.1", "agnostic.2"],
        )
        assert err is None
        # Caller pairs verdicts with the expected_ids list, so the
        # parser must align the response to that order.
        assert verdicts[0]["id"] == "agnostic.1"
        assert verdicts[1]["id"] == "agnostic.2"


# ---------------------------------------------------------------------------
# End-to-end grading with a mocked urlopen.
# ---------------------------------------------------------------------------

class TestGradeTemplate:
    def _load_k1(self):
        loader = YAMLLoader()
        template = loader.load_template(K1_SAMPLE)
        gen = TemplateGenerator(templates_dir=TEMPLATES_DIR)
        return template, gen

    def test_all_pass_emits_one_finding_per_item_per_seed(self):
        template, gen = self._load_k1()
        items = items_for("all", with_image=False)

        def fake_urlopen(req, timeout=None):
            return _ollama_response([
                {"id": it.id, "pass": True, "note": ""}
                for it in items
            ])

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            findings = grade_template(
                template, gen,
                model="qwen3.5:0.8b",
                samples_per_template=2,
                seed_base=0,
                rubric_set="all",
                with_image=False,
            )

        # 2 seeds × len(items) info findings, all pass=True.
        assert len(findings) == 2 * len(items)
        assert all(f.severity == "info" for f in findings)
        assert all(f.extra["pass"] is True for f in findings)
        rules = {f.rule for f in findings}
        for it in items:
            assert f"grading.{it.id}" in rules

    def test_some_fail_emit_error_severity(self):
        template, gen = self._load_k1()
        items = items_for("all", with_image=False)

        def fake_urlopen(req, timeout=None):
            payload = []
            for i, it in enumerate(items):
                payload.append({
                    "id": it.id,
                    "pass": i % 2 == 0,
                    "note": "" if i % 2 == 0 else "bad",
                })
            return _ollama_response(payload)

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            findings = grade_template(
                template, gen,
                model="qwen3.5:0.8b",
                samples_per_template=1,
                rubric_set="all",
                with_image=False,
            )

        errors = [f for f in findings if f.severity == "error"]
        assert errors, "expected at least one fail finding"
        assert all("note" in f.extra for f in errors)

    def test_parse_error_after_one_retry(self):
        template, gen = self._load_k1()

        # Both attempts return junk → parse_error finding.
        def fake_urlopen(req, timeout=None):
            return _FakeResp(b'{"response": "totally not json"}')

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            findings = grade_template(
                template, gen,
                model="qwen3.5:0.8b",
                samples_per_template=1,
                rubric_set="agnostic",
                with_image=False,
            )

        assert any(f.rule == "grading.parse_error" for f in findings)
        # No item-level findings emitted when parse fails.
        item_findings = [f for f in findings if f.rule.startswith("grading.agnostic")]
        assert item_findings == []

    def test_retry_succeeds_on_second_attempt(self):
        template, gen = self._load_k1()
        items = items_for("agnostic", with_image=False)

        good = json.dumps({"items": [
            {"id": it.id, "pass": True, "note": ""} for it in items
        ]})
        responses = iter([
            _FakeResp(b'{"response": "garbage"}'),
            _FakeResp(json.dumps({"response": good}).encode("utf-8")),
        ])

        with patch("urllib.request.urlopen", side_effect=lambda req, timeout=None: next(responses)):
            findings = grade_template(
                template, gen,
                model="qwen3.5:0.8b",
                samples_per_template=1,
                rubric_set="agnostic",
                with_image=False,
            )

        assert len(findings) == len(items)
        assert all(f.severity == "info" for f in findings)

    def test_falls_back_to_thinking_field_when_response_empty(self):
        """qwen3.5:* with `think:true` puts its answer in the `thinking`
        channel and leaves `response` empty. The grader treats `thinking`
        as a fallback so those models don't always parse_error."""
        template, gen = self._load_k1()
        items = items_for("agnostic", with_image=False)
        good_inner = json.dumps({"items": [
            {"id": it.id, "pass": True, "note": ""} for it in items
        ]})
        envelope = json.dumps({"response": "", "thinking": good_inner})

        def fake_urlopen(req, timeout=None):
            return _FakeResp(envelope.encode("utf-8"))

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            findings = grade_template(
                template, gen,
                samples_per_template=1,
                rubric_set="agnostic",
                with_image=False,
            )

        assert len(findings) == len(items)
        assert all(f.severity == "info" for f in findings)

    def test_non_k1_template_skipped_when_rubric_is_k1(self):
        # Pick any non-K1 template — fall back to a known K3+ if available.
        higher = TEMPLATES_DIR / "geometry" / "k5_easy_square_area_01_anchor.yaml"
        if not higher.exists():
            pytest.skip("no >K1 template available for this test")
        loader = YAMLLoader()
        template = loader.load_template(higher)
        gen = TemplateGenerator(templates_dir=TEMPLATES_DIR)

        # No urlopen calls expected since K1 rubric is skipped.
        with patch("urllib.request.urlopen", side_effect=AssertionError("should not call")):
            findings = grade_template(
                template, gen,
                rubric_set="k1",
                with_image=False,
                samples_per_template=1,
            )

        assert len(findings) == 1
        assert findings[0].rule == "grading.skipped"


# ---------------------------------------------------------------------------
# Path-level dispatch.
# ---------------------------------------------------------------------------

class TestGradePath:
    def test_single_file_grade_filter_skips(self):
        """`grade_path` with grade_filter=1 against a non-K1 file returns
        only loader findings (no item findings, no traceback)."""
        higher = TEMPLATES_DIR / "geometry" / "k5_easy_square_area_01_anchor.yaml"
        if not higher.exists():
            pytest.skip("no >K1 template available")

        with patch("urllib.request.urlopen", side_effect=AssertionError("should not call")):
            findings = grade_path(
                higher,
                samples_per_template=1,
                rubric_set="all",
                with_image=False,
                grade_filter=1,
            )

        # No grading.* item findings produced; loader findings (if any)
        # would be schema_invalid or similar — not grading rules.
        item_findings = [f for f in findings if f.rule.startswith("grading.")]
        assert item_findings == []


# ---------------------------------------------------------------------------
# γ.4r R.1 — grader-side determinism overrides.
# ---------------------------------------------------------------------------

class TestK14WordCountOverride:
    """R.1a — K1.4 prose-length is decided client-side by an actual word
    count of the rendered body, overriding any model hallucination."""

    def _setup(self):
        loader = YAMLLoader()
        template = loader.load_template(K1_SAMPLE)
        gen = TemplateGenerator(templates_dir=TEMPLATES_DIR)
        return template, gen

    def test_long_prose_fails_even_when_model_says_pass(self):
        template, gen = self._setup()
        items = items_for("k1", with_image=False)
        # Model lies — every item passes, including K1.4.
        def fake_urlopen(req, timeout=None):
            return _ollama_response([
                {"id": it.id, "pass": True, "note": ""}
                for it in items
            ])
        # Patch render_samples to return a 30-word body.
        long_body = " ".join(["word"] * 30)
        from src.audit.render import RenderedSample
        fake_samples = [RenderedSample(
            template_id=template.id, seed=0, tier="easy",
            body=long_body, answer="5", raw={},
        )]
        with patch("urllib.request.urlopen", side_effect=fake_urlopen), \
             patch("src.grading.grader.render_samples", return_value=fake_samples):
            findings = grade_template(
                template, gen,
                samples_per_template=1,
                rubric_set="k1",
                with_image=False,
            )
        k14 = [f for f in findings if f.rule == "grading.k1.4"]
        assert len(k14) == 1
        assert k14[0].severity == "error"
        assert "30 words" in k14[0].extra["note"]

    def test_short_prose_passes_even_when_model_says_fail(self):
        template, gen = self._setup()
        items = items_for("k1", with_image=False)
        # Model lies — every item fails, including K1.4 with a hallucinated count.
        def fake_urlopen(req, timeout=None):
            return _ollama_response([
                {
                    "id": it.id,
                    "pass": False,
                    "note": (
                        "Prose is 26 words, exceeding 25-word limit"
                        if it.id == "k1.4" else "fail"
                    ),
                }
                for it in items
            ])
        short_body = "Tom has 5 apples."  # 4 words
        from src.audit.render import RenderedSample
        fake_samples = [RenderedSample(
            template_id=template.id, seed=0, tier="easy",
            body=short_body, answer="5", raw={},
        )]
        with patch("urllib.request.urlopen", side_effect=fake_urlopen), \
             patch("src.grading.grader.render_samples", return_value=fake_samples):
            findings = grade_template(
                template, gen,
                samples_per_template=1,
                rubric_set="k1",
                with_image=False,
            )
        k14 = [f for f in findings if f.rule == "grading.k1.4"]
        assert len(k14) == 1
        assert k14[0].severity == "info"
        assert k14[0].extra["pass"] is True
        assert k14[0].extra["note"] == ""

    def test_exactly_25_words_passes(self):
        template, gen = self._setup()
        items = items_for("k1", with_image=False)
        def fake_urlopen(req, timeout=None):
            return _ollama_response([
                {"id": it.id, "pass": True, "note": ""} for it in items
            ])
        body_25 = " ".join(["word"] * 25)
        from src.audit.render import RenderedSample
        fake_samples = [RenderedSample(
            template_id=template.id, seed=0, tier="easy",
            body=body_25, answer="5", raw={},
        )]
        with patch("urllib.request.urlopen", side_effect=fake_urlopen), \
             patch("src.grading.grader.render_samples", return_value=fake_samples):
            findings = grade_template(
                template, gen,
                samples_per_template=1, rubric_set="k1", with_image=False,
            )
        k14 = [f for f in findings if f.rule == "grading.k1.4"]
        assert len(k14) == 1
        assert k14[0].severity == "info"


class TestNoteStripping:
    """R.1c — leading 'No image attached;' / 'No image present;' is
    stripped from notes so cross-seed dedup works on the substantive
    text."""

    def _setup(self):
        loader = YAMLLoader()
        template = loader.load_template(K1_SAMPLE)
        gen = TemplateGenerator(templates_dir=TEMPLATES_DIR)
        return template, gen

    def test_strips_leading_no_image_attached(self):
        template, gen = self._setup()
        items = items_for("all", with_image=False)
        def fake_urlopen(req, timeout=None):
            return _ollama_response([
                {
                    "id": it.id, "pass": False,
                    "note": "No image attached; visual quantity cannot be verified.",
                }
                for it in items
            ])
        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            findings = grade_template(
                template, gen,
                samples_per_template=1, rubric_set="all", with_image=False,
            )
        # Pick one item that the model produced output for (the K1.4
        # override drops out).
        for f in findings:
            if f.rule == "grading.k1.4":
                continue  # K1.4 is overridden and gets a different note
            assert not f.extra["note"].startswith("No image"), (
                f"unstripped: {f.extra['note']!r} on {f.rule}"
            )

    def test_strips_no_image_present_variant(self):
        template, gen = self._setup()
        items = items_for("agnostic", with_image=False)
        def fake_urlopen(req, timeout=None):
            return _ollama_response([
                {
                    "id": it.id, "pass": False,
                    "note": "No image present; prose alone insufficient for K1.",
                }
                for it in items
            ])
        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            findings = grade_template(
                template, gen,
                samples_per_template=1,
                rubric_set="agnostic",
                with_image=False,
            )
        for f in findings:
            assert "prose alone insufficient" in f.extra["note"]
            assert not f.extra["note"].startswith("No image")

    def test_note_without_prefix_unchanged(self):
        template, gen = self._setup()
        items = items_for("agnostic", with_image=False)
        original_note = "Topic 'measurement.time' misaligned with recall fact."
        def fake_urlopen(req, timeout=None):
            return _ollama_response([
                {"id": it.id, "pass": False, "note": original_note}
                for it in items
            ])
        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            findings = grade_template(
                template, gen,
                samples_per_template=1,
                rubric_set="agnostic",
                with_image=False,
            )
        for f in findings:
            assert f.extra["note"] == original_note
