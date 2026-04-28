"""Tests for `src/audit/` — the corpus self-check package backing
`mathbot lint` and `mathbot health`.

Strategy: build a small synthetic template corpus in `tmp_path` per
test, render through the real `TemplateGenerator`, and assert the
expected findings appear. Keeps test isolation tight without mocking.

The real corpus smoke test is small but valuable: it exercises the
full pipeline on every shipped template and asserts no `error`-severity
findings — catching regressions in any rule (or the renderer) at
test time.
"""

import yaml
import pytest

from src.audit import (
    Finding, count_by_severity,
    coverage_rows, coverage_summary,
    cross_template_contamination,
    find_near_dupes, lint_path, normalize_for_dupes,
    run_health,
)
from src.audit.contamination import jaccard, shingles
from src.audit.render import RenderedSample


# ---------------------------------------------------------------------------
# Helpers — build a minimal valid template on disk.
# ---------------------------------------------------------------------------

def _write_template(
    base: "Path", topic_dir: str, filename: str, *, body: str = "{{a}} + {{b}} = ?",
    solution: str = "Answer = a + b", variables=None, metadata_overrides=None,
    answer_type: str = "integer", tests=None, expected_answer: str = "2",
):
    """Write a tiny addition template with deterministic a=b=1 → Answer=2.

    Hard-coded `min=max=1` so the embedded test fixture matches the
    generated answer regardless of seed; saves tests from computing the
    expected per (variables, seed) pair.
    """
    from pathlib import Path
    topic = Path(base) / topic_dir
    topic.mkdir(parents=True, exist_ok=True)
    metadata = {
        "id": filename.removesuffix(".yaml"),
        "version": "1.0.0",
        "author": "t",
        "created": "2026-04-27",
        "grade": 1,
        "topic": f"{topic_dir}.addition",
        "family": "addition",
        "difficulty": "easy",
        "steps": 1,
    }
    if metadata_overrides:
        metadata.update(metadata_overrides)
    vars_ = variables or {
        "a": {"type": "integer", "min": 1, "max": 1},
        "b": {"type": "integer", "min": 1, "max": 1},
        "Answer": {"type": answer_type},
    }
    payload = {
        "metadata": metadata,
        "variables": vars_,
        "template": body,
        "solution": solution,
        "tests": (
            tests if tests is not None
            else [{"seed": 1, "expected": {"answer": expected_answer}}]
        ),
    }
    (topic / filename).write_text(yaml.safe_dump(payload, sort_keys=False))
    return topic / filename


# ---------------------------------------------------------------------------
# Coverage matrix
# ---------------------------------------------------------------------------

class TestCoverage:
    def test_coverage_buckets_by_cell(self, tmp_path):
        _write_template(tmp_path, "arithmetic", "k1_easy_addition_01_anchor.yaml")
        _write_template(tmp_path, "arithmetic", "k1_easy_addition_02.yaml")
        _write_template(tmp_path, "arithmetic", "k2_easy_addition_01_anchor.yaml",
                        metadata_overrides={"grade": 2, "id": "k2_easy_addition_01"})

        from src.yaml_loader import load_all_templates
        templates = load_all_templates(tmp_path)
        rows = coverage_rows(templates.values())
        summary = coverage_summary(rows)

        assert summary == {"cells": 2, "anchors": 2, "variants": 1, "total": 3}
        # Two cells: k1 (2 templates: 1 anchor + 1 variant), k2 (1 anchor).
        k1_row = next(r for r in rows if r["grade"] == "k1")
        k2_row = next(r for r in rows if r["grade"] == "k2")
        assert k1_row == {
            "grade": "k1", "topic": "arithmetic.addition", "family": "addition",
            "difficulty": "easy", "count": 2, "anchor_count": 1, "variant_count": 1,
        }
        assert k2_row["count"] == 1 and k2_row["anchor_count"] == 1


# ---------------------------------------------------------------------------
# Within-cell near-dupes
# ---------------------------------------------------------------------------

class TestDupes:
    def test_normalize_for_dupes_strips_numbers_and_names(self):
        # Numbers → <N>, capitalized words → <W>, whitespace collapsed.
        # Pronouns (lowercase) are NOT stripped — the normalization is
        # similarity-skeleton, not full anonymization.
        a = "Alice has 5 apples. They get 2 more."
        b = "Bob has 7 apples. They get 3 more."
        assert normalize_for_dupes(a) == normalize_for_dupes(b)
        # And numbers / names get replaced visibly:
        assert "<n>" in normalize_for_dupes("I have 5 apples")
        assert "<w>" in normalize_for_dupes("Alice ate them")

    def test_find_near_dupes_within_cell(self):
        cell = ("k1", "arithmetic.addition", "addition")
        a = RenderedSample("a_id", 0, "easy",
                           "Alice has 5 apples. She gets 3 more.", "8", {})
        b = RenderedSample("b_id", 0, "easy",
                           "Bob has 7 apples. He gets 2 more.", "9", {})
        c = RenderedSample("c_id", 0, "easy",
                           "Compute the area of a square with side 4.", "16 m²", {})
        cell_of = {"a_id": cell, "b_id": cell, "c_id": cell}
        complexity = {"a_id": 1, "b_id": 1, "c_id": 1}
        pairs = find_near_dupes([a, b, c], cell_of, complexity)
        ids = {(p["pid_a"], p["pid_b"]) for p in pairs}
        assert ("a_id", "b_id") in ids or ("b_id", "a_id") in ids
        # The unrelated geometry sentence should not pair with either.
        assert not any("c_id" in (p["pid_a"], p["pid_b"]) for p in pairs)


# ---------------------------------------------------------------------------
# Cross-template internal contamination
# ---------------------------------------------------------------------------

class TestContamination:
    def test_jaccard_basic(self):
        assert jaccard(set(), set()) == 0.0
        assert jaccard({1, 2, 3}, {1, 2, 3}) == 1.0
        assert jaccard({1, 2}, {2, 3}) == 1 / 3

    def test_shingles_n5(self):
        s = shingles("the quick brown fox jumps over", 5)
        # 6 tokens → 2 5-grams
        assert len(s) == 2

    def test_cross_template_contamination_top_pairs(self):
        # Two near-identical samples should rank top.
        a = RenderedSample("a_id", 0, "easy",
                           "Sarah went shopping and bought five red apples for two dollars each.", "", {})
        b = RenderedSample("b_id", 0, "easy",
                           "Sarah went shopping and bought five green apples for three dollars each.", "", {})
        c = RenderedSample("c_id", 0, "easy",
                           "Compute the volume of a cylinder with radius and height given.", "", {})
        report = cross_template_contamination([a, b, c], n_gram=3, top_pairs=10)
        assert report["summary"]["templates_analyzed"] == 3
        # a_id × b_id should be the highest-similarity pair (overlap on
        # "Sarah went shopping", "and bought five", etc.). Threshold is
        # generous because n=3 on short text gives low absolute Jaccard.
        top = report["top_pairs"][0]
        assert {top["a"], top["b"]} == {"a_id", "b_id"}
        assert top["similarity"] > 0.2


# ---------------------------------------------------------------------------
# Lint rules — one synthetic template per rule.
# ---------------------------------------------------------------------------

class TestLintRules:
    def test_render_smoke_passes_for_clean_template(self, tmp_path):
        path = _write_template(tmp_path, "arithmetic", "k1_easy_addition_01_anchor.yaml")
        findings = lint_path(path, samples_per_template=2)
        # Clean template emits no error-severity findings.
        assert count_by_severity(findings)["error"] == 0

    def test_unrendered_jinja_fires_when_solution_var_used_in_template(self, tmp_path):
        # Solution-only variable used in template body without `{% set %}`.
        # The Jinja renderer with default `Undefined` silently emits empty,
        # so the literal `{{...}}` won't survive — we instead test the
        # detector directly by rendering text that DOES contain `{{...}}`
        # (e.g. a problem template that escaped Jinja with `{% raw %}`).
        path = _write_template(
            tmp_path, "arithmetic", "k1_easy_unrendered_anchor.yaml",
            body="{% raw %}{{leftover}}{% endraw %}",
            solution="Answer = a + b",
        )
        findings = lint_path(path, samples_per_template=1)
        assert any(f.rule == "unrendered_jinja" and f.severity == "error" for f in findings)

    def test_empty_answer_fires_when_answer_blank(self, tmp_path):
        path = _write_template(
            tmp_path, "arithmetic", "k1_easy_empty_anchor.yaml",
            answer_type="string",
            solution="Answer = ''",  # blank
            expected_answer="",
        )
        findings = lint_path(path, samples_per_template=1)
        assert any(f.rule == "empty_answer" and f.severity == "error" for f in findings)

    def test_body_too_long_fires(self, tmp_path):
        # A template body padded to exceed the threshold.
        long_body = "x " * 500 + "{{a}} + {{b}} = ?"
        path = _write_template(
            tmp_path, "arithmetic", "k1_easy_long_anchor.yaml",
            body=long_body,
        )
        findings = lint_path(path, samples_per_template=1)
        assert any(f.rule == "body_too_long" for f in findings)

    def test_render_crash_fires_on_solution_exception(self, tmp_path):
        path = _write_template(
            tmp_path, "arithmetic", "k1_easy_crash_anchor.yaml",
            solution="Answer = 1 / 0",  # raises ZeroDivisionError at render time
        )
        findings = lint_path(path, samples_per_template=2)
        assert any(f.rule == "render_crash" for f in findings)

    def test_fixture_missing_when_no_tests(self, tmp_path):
        path = _write_template(
            tmp_path, "arithmetic", "k1_easy_notests_anchor.yaml",
            tests=[],
        )
        findings = lint_path(path, samples_per_template=1)
        assert any(f.rule == "fixture_missing" for f in findings)

    def test_off_anchor_divergence_fires(self, tmp_path):
        # Anchor with steps=1, variant in same cell with steps=5.
        _write_template(tmp_path, "arithmetic", "k1_easy_addition_01_anchor.yaml")
        _write_template(
            tmp_path, "arithmetic", "k1_easy_addition_02.yaml",
            metadata_overrides={"id": "k1_easy_addition_02", "steps": 5},
        )
        findings = lint_path(tmp_path, samples_per_template=1)
        # Variant should fire off_anchor_divergence (steps mismatch).
        assert any(
            f.rule == "off_anchor_divergence"
            and f.template_id == "k1_easy_addition_02"
            for f in findings
        )

    def test_anchor_filename_mismatch_fires_for_dual_anchors(self, tmp_path):
        _write_template(tmp_path, "arithmetic", "k1_easy_addition_01_anchor.yaml")
        _write_template(
            tmp_path, "arithmetic", "k1_easy_addition_02_anchor.yaml",
            metadata_overrides={"id": "k1_easy_addition_02"},
        )
        findings = lint_path(tmp_path, samples_per_template=1)
        # The runner picks one as the anchor (whichever is iterated first);
        # the other should fire anchor_filename_mismatch.
        mismatches = [f for f in findings if f.rule == "anchor_filename_mismatch"]
        assert len(mismatches) == 1


# ---------------------------------------------------------------------------
# Health — corpus-level pipeline
# ---------------------------------------------------------------------------

class TestHealth:
    def test_run_health_smoke_synthetic_corpus(self, tmp_path):
        _write_template(tmp_path, "arithmetic", "k1_easy_addition_01_anchor.yaml")
        _write_template(tmp_path, "arithmetic", "k2_easy_addition_01_anchor.yaml",
                        metadata_overrides={"grade": 2, "id": "k2_easy_addition_01"})
        report = run_health(tmp_path, samples_per_template=2)
        assert report["coverage"]["summary"]["total"] == 2
        # Both templates rendered, contamination summary is well-formed.
        cont = report["contamination"]["summary"]
        assert cont["templates_analyzed"] == 2
        assert "max" in cont and "p95" in cont


# ---------------------------------------------------------------------------
# Real corpus smoke test
# ---------------------------------------------------------------------------

class TestRealCorpus:
    """End-to-end smoke against the shipped templates.

    Asserts no `error`-severity findings — catches regressions in any
    rule (or the renderer) without freezing the warning/info counts
    (which authoring naturally fluctuates).
    """

    def test_full_corpus_no_errors(self):
        from pathlib import Path
        templates_dir = Path(__file__).parent.parent / "src" / "templates"
        if not templates_dir.is_dir():
            pytest.skip("no shipped templates dir")
        from src.audit import lint_corpus
        findings = lint_corpus(templates_dir, samples_per_template=2)
        errors = [f for f in findings if f.severity == "error"]
        assert errors == [], (
            f"corpus has {len(errors)} error-severity findings:\n"
            + "\n".join(f"  {f.rule} on {f.template_id}: {f.message}" for f in errors[:10])
        )
