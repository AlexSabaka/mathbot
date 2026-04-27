"""Tests for Phase 5.7 multi-tier templates.

A multi-tier template declares `metadata.difficulty_tiers: [...]` and
ships per-difficulty `ranges:` on its variable specs. The generator
selects an effective tier per render (via `--complexity` or random
sampling) and looks up min/max/step/choices in `spec.ranges[tier]`,
falling back to the flat fields when the tier isn't listed. Single-tier
templates are unaffected.
"""

import textwrap
from pathlib import Path

import pytest

from src.template_generator import TemplateGenerator
from src.variable_generator import VariableGenerator
from src.yaml_loader import VariableSpec, YAMLLoader


# ---------------------------------------------------------------------------
# VariableSpec.ranges + VariableGenerator difficulty threading.
# ---------------------------------------------------------------------------


class TestPerTierRanges:
    """Per-tier `ranges` override flat min/max/step/choices."""

    def test_integer_uses_tier_range(self):
        spec = VariableSpec(
            name="n",
            type="integer",
            min=1,
            max=5,
            ranges={
                "easy": {"min": 1, "max": 5},
                "medium": {"min": 50, "max": 100},
                "hard": {"min": 500, "max": 1000},
            },
        )
        g = VariableGenerator(seed=1)
        for _ in range(20):
            assert 1 <= g._generate_integer(spec, difficulty="easy") <= 5
        for _ in range(20):
            assert 50 <= g._generate_integer(spec, difficulty="medium") <= 100
        for _ in range(20):
            assert 500 <= g._generate_integer(spec, difficulty="hard") <= 1000

    def test_falls_back_to_flat_when_tier_missing(self):
        # `hard` not declared → flat min/max apply.
        spec = VariableSpec(
            name="n",
            type="integer",
            min=1,
            max=5,
            ranges={"easy": {"min": 100, "max": 200}},
        )
        g = VariableGenerator(seed=1)
        for _ in range(20):
            assert 1 <= g._generate_integer(spec, difficulty="hard") <= 5

    def test_no_difficulty_uses_flat(self):
        # Existing single-tier path: difficulty=None ignores `ranges`.
        spec = VariableSpec(
            name="n",
            type="integer",
            min=1,
            max=5,
            ranges={"easy": {"min": 100, "max": 200}},
        )
        g = VariableGenerator(seed=1)
        for _ in range(20):
            assert 1 <= g._generate_integer(spec) <= 5

    def test_per_tier_choices(self):
        spec = VariableSpec(
            name="p",
            type="integer",
            ranges={
                "easy": {"choices": [10, 100]},
                "medium": {"choices": [10, 100, 1000]},
            },
        )
        g = VariableGenerator(seed=1)
        for _ in range(20):
            assert g._generate_integer(spec, difficulty="easy") in {10, 100}
        for _ in range(20):
            assert g._generate_integer(spec, difficulty="medium") in {10, 100, 1000}

    def test_decimal_uses_tier_step(self):
        spec = VariableSpec(
            name="d",
            type="decimal",
            min=0.1,
            max=99.9,
            step=0.01,
            ranges={"hard": {"step": 0.001}},
        )
        g = VariableGenerator(seed=1)
        # Sample many at hard tier; at step=0.001, third decimal is meaningful.
        # Sanity-check: the value lands within the range.
        for _ in range(50):
            v = g._generate_decimal(spec, difficulty="hard")
            assert 0.1 <= v <= 99.9


# ---------------------------------------------------------------------------
# YAML schema parsing & validation for multi-tier metadata.
# ---------------------------------------------------------------------------


def _write_template(tmp_path: Path, body: str) -> Path:
    p = tmp_path / "t.yaml"
    p.write_text(textwrap.dedent(body).lstrip())
    return p


class TestSchemaValidation:
    """`difficulty_tiers` must include default difficulty; `ranges` keys must
    be valid tier names."""

    def _parent_template_under_arithmetic(self, tmp_path: Path) -> Path:
        # The loader enforces topic ↔ directory invariant; build the file
        # under an `arithmetic/` subdir so `topic: arithmetic.basic` checks.
        sub = tmp_path / "arithmetic"
        sub.mkdir()
        return sub

    def test_parses_difficulty_tiers(self, tmp_path):
        sub = self._parent_template_under_arithmetic(tmp_path)
        p = sub / "k1_easy_x.yaml"
        p.write_text(textwrap.dedent("""
            metadata:
              id: k1_easy_x
              version: "1.0.0"
              author: Test
              created: 2026-04-27
              grade: 1
              topic: arithmetic.basic
              family: addition
              difficulty: easy
              difficulty_tiers: [easy, medium]
              steps: 1
            variables:
              n:
                type: integer
                ranges:
                  easy:  {min: 1, max: 5}
                  medium: {min: 50, max: 100}
              Answer:
                type: integer
            template: "Add {{n}} and {{n}}."
            solution: "Answer = n + n"
        """).lstrip())
        loader = YAMLLoader()
        t = loader.load_template(p)
        assert t is not None, loader.errors
        assert t.difficulty_tiers == ["easy", "medium"]
        assert t.variables["n"].ranges == {
            "easy":   {"min": 1, "max": 5},
            "medium": {"min": 50, "max": 100},
        }

    def test_difficulty_tiers_must_include_default(self, tmp_path):
        sub = self._parent_template_under_arithmetic(tmp_path)
        p = sub / "k1_easy_x.yaml"
        p.write_text(textwrap.dedent("""
            metadata:
              id: k1_easy_x
              version: "1.0.0"
              author: Test
              created: 2026-04-27
              grade: 1
              topic: arithmetic.basic
              family: addition
              difficulty: easy
              difficulty_tiers: [medium, hard]
              steps: 1
            variables:
              Answer:
                type: integer
            template: "x"
            solution: "Answer = 1"
        """).lstrip())
        loader = YAMLLoader()
        assert loader.load_template(p) is None
        assert any("must include the default" in e for e in loader.errors)

    def test_invalid_tier_in_ranges_rejected(self, tmp_path):
        sub = self._parent_template_under_arithmetic(tmp_path)
        p = sub / "k1_easy_x.yaml"
        p.write_text(textwrap.dedent("""
            metadata:
              id: k1_easy_x
              version: "1.0.0"
              author: Test
              created: 2026-04-27
              grade: 1
              topic: arithmetic.basic
              family: addition
              difficulty: easy
              steps: 1
            variables:
              n:
                type: integer
                ranges:
                  insane: {min: 1, max: 5}
              Answer:
                type: integer
            template: "x"
            solution: "Answer = 1"
        """).lstrip())
        loader = YAMLLoader()
        assert loader.load_template(p) is None
        assert any("not a valid difficulty" in e for e in loader.errors)


# ---------------------------------------------------------------------------
# Test-id stability and effective-difficulty in rendered output.
# ---------------------------------------------------------------------------


@pytest.fixture
def multitier_template_dir(tmp_path: Path) -> Path:
    """Build a one-template `arithmetic/` corpus the TemplateGenerator can load."""
    root = tmp_path / "templates"
    sub = root / "arithmetic"
    sub.mkdir(parents=True)
    (sub / "k1_easy_addmt_anchor.yaml").write_text(textwrap.dedent("""
        metadata:
          id: k1_easy_addmt
          version: "1.0.0"
          author: Test
          created: 2026-04-27
          grade: 1
          topic: arithmetic.basic
          family: addition
          difficulty: easy
          difficulty_tiers: [easy, medium, hard]
          steps: 1
        variables:
          a:
            type: integer
            ranges:
              easy:   {min: 1, max: 9}
              medium: {min: 10, max: 99}
              hard:   {min: 100, max: 999}
          b:
            type: integer
            ranges:
              easy:   {min: 1, max: 9}
              medium: {min: 10, max: 99}
              hard:   {min: 100, max: 999}
          Answer:
            type: integer
        template: "Add {{a}} and {{b}}."
        solution: "Answer = a + b"
        tests:
          - seed: 1
            difficulty: easy
            expected: {answer: "auto"}
          - seed: 2
            difficulty: medium
            expected: {answer: "auto"}
    """).lstrip())
    return root


class TestRenderingMultiTier:
    def test_test_id_carries_tier_suffix(self, multitier_template_dir):
        gen = TemplateGenerator(templates_dir=multitier_template_dir, seed=1)
        for tier, complexity in [("easy", 1), ("medium", 2), ("hard", 3)]:
            out = gen.generate(complexity=complexity)
            assert out["test_id"] == f"math_k1_easy_addmt__{tier}"
            assert out["task_params"]["complexity"] == complexity

    def test_per_tier_ranges_drive_value_magnitude(self, multitier_template_dir):
        gen = TemplateGenerator(templates_dir=multitier_template_dir, seed=42)
        easy = gen.generate(complexity=1, seed=42)
        hard = gen.generate(complexity=3, seed=42)
        # Easy answer is single-digit + single-digit: max 18; hard answer is
        # 3-digit + 3-digit: min 200.
        assert int(easy["task_params"]["expected_answer"]) <= 18
        assert int(hard["task_params"]["expected_answer"]) >= 200

    def test_config_name_reflects_effective_tier(self, multitier_template_dir):
        gen = TemplateGenerator(templates_dir=multitier_template_dir, seed=1)
        out = gen.generate(complexity=3)
        assert "_hard_" in out["config_name"]


class TestSingleTierBackCompat:
    """Templates without `difficulty_tiers` keep their historical test_id."""

    def test_test_id_unchanged_for_single_tier(self, tmp_path):
        root = tmp_path / "templates"
        sub = root / "arithmetic"
        sub.mkdir(parents=True)
        (sub / "k1_easy_legacy.yaml").write_text(textwrap.dedent("""
            metadata:
              id: k1_easy_legacy
              version: "1.0.0"
              author: Test
              created: 2026-04-27
              grade: 1
              topic: arithmetic.basic
              family: addition
              difficulty: easy
              steps: 1
            variables:
              a: {type: integer, min: 1, max: 9}
              Answer: {type: integer}
            template: "{{a}}"
            solution: "Answer = a"
        """).lstrip())
        gen = TemplateGenerator(templates_dir=root, seed=1)
        out = gen.generate(complexity=1)
        # No __<tier> suffix on legacy templates.
        assert out["test_id"] == "math_k1_easy_legacy"
