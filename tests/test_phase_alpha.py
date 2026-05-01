"""Phase α (B1–B5) infrastructure tests.

Covers the foundation work landed before P0 mass-authoring of v2
(MATHBOT_PROBLEMS_PROPOSAL_v2.md) begins:

- B1: symbolic answer canonicalization in `format_answer` for
  `sympy.Expr`, `sympy.Matrix`, and `complex` Answers.
- B2: `track:` metadata field on `TemplateDefinition` plus the
  `track_missing` lint rule for K9+ templates.
- B3/B4: `compare:` (string|numeric|symbolic) and
  `tolerance:`/`tolerance_rel:` on `TestCase`, dispatched through the
  shared `compare_answers` helper used by both `mathbot test` and
  `mathbot lint`.
- B5: new K9–K12 family / topic / topic-grade entries in `constants.py`.
"""

from pathlib import Path

import pytest
import sympy as sp
import yaml

from src.audit import lint_path
from src.constants import (
    FAMILY_TOPIC_SUPPORT,
    MATH_TOPICS,
    PROBLEM_FAMILIES,
    TOPIC_GRADE_COMPATIBILITY,
)
from src.solution_evaluator import compare_answers, format_answer
from src.yaml_loader import TemplateDefinition, YAMLLoader, VariableSpec


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_minimal(tmp_path: Path, **metadata_overrides):
    """Drop a syntactically valid k1 addition template into tmp_path.

    Returns the file's path. Uses min=max=1 so a=b=1 → Answer=2 stably,
    letting the lint runner verify embedded fixtures without seed-tuning.
    """
    topic_dir = tmp_path / "arithmetic"
    topic_dir.mkdir(parents=True, exist_ok=True)
    metadata = {
        "id": metadata_overrides.get("id", "k1_easy_addition_01"),
        "version": "1.0.0",
        "author": "t",
        "created": "2026-04-27",
        "grade": 1,
        "topic": "arithmetic.addition",
        "family": "addition",
        "difficulty": "easy",
        "steps": 1,
    }
    metadata.update(metadata_overrides)
    payload = {
        "metadata": metadata,
        "variables": {
            "a": {"type": "integer", "min": 1, "max": 1},
            "b": {"type": "integer", "min": 1, "max": 1},
            "Answer": {"type": "integer"},
        },
        "template": "{{a}} + {{b}} = ?",
        "solution": "Answer = a + b",
        "tests": [{"seed": 1, "expected": {"answer": "2"}}],
    }
    path = topic_dir / f"{metadata['id']}.yaml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False))
    return path


# ---------------------------------------------------------------------------
# B5 — constants.py family / topic / topic-grade entries
# ---------------------------------------------------------------------------

class TestB5Constants:
    """v2 N1–N16 family entries plus the new top-level topics."""

    @pytest.mark.parametrize("family", [
        "function_transformation",
        "polynomial_operations",
        "quadratic_method_selection",
        "sequence_series",
        "absolute_value_piecewise",
        "conic_application",
        "complex_application",
        "logarithmic_inversion",
        "matrix_application",
        "vector_application",
        "trig_identity_application",
        "limit_application",
        "derivative_application",
        "integral_application",
        "first_order_ode",
        "second_order_ode",
    ])
    def test_n_family_present(self, family):
        assert family in PROBLEM_FAMILIES
        assert family in FAMILY_TOPIC_SUPPORT, (
            f"family '{family}' has no FAMILY_TOPIC_SUPPORT entry — CLI "
            f"--family / --topic compatibility checks will skip it"
        )

    @pytest.mark.parametrize("topic", [
        "sequences",
        "trigonometry",
        "linear_algebra",
        "calculus",
        "differential_equations",
    ])
    def test_new_topic_in_compat_table(self, topic):
        assert topic in MATH_TOPICS
        assert topic in TOPIC_GRADE_COMPATIBILITY, (
            f"new topic '{topic}' missing from TOPIC_GRADE_COMPATIBILITY"
        )

    def test_every_family_supports_at_least_one_topic(self):
        # Sanity check: a family with no topic support is dead code from
        # the CLI's perspective.
        unsupported = [
            f for f in PROBLEM_FAMILIES if not FAMILY_TOPIC_SUPPORT.get(f)
        ]
        assert unsupported == [], unsupported


# ---------------------------------------------------------------------------
# B2 — track: metadata field
# ---------------------------------------------------------------------------

class TestB2TrackField:
    def test_track_defaults_to_none(self):
        td = TemplateDefinition(
            id="x", version="1", author="a", created="2026-04-27",
            grade=1, topic="arithmetic.addition", family="addition",
            difficulty="easy", steps=1,
        )
        assert td.track is None

    @pytest.mark.parametrize("track", sorted(YAMLLoader.VALID_TRACKS))
    def test_valid_track_loads(self, tmp_path, track):
        path = _write_minimal(tmp_path, track=track)
        loader = YAMLLoader()
        tpl = loader.load_template(path)
        assert tpl is not None, loader.errors
        assert tpl.track == track

    def test_invalid_track_rejected(self, tmp_path):
        path = _write_minimal(tmp_path, track="tetiary")  # typo
        loader = YAMLLoader()
        tpl = loader.load_template(path)
        assert tpl is None
        assert any("metadata.track" in e for e in loader.errors)

    def test_track_missing_lint_skips_k1(self, tmp_path):
        _write_minimal(tmp_path, grade=1)
        findings = lint_path(tmp_path)
        track_findings = [f for f in findings if f.rule == "track_missing"]
        assert track_findings == []

    def test_track_missing_lint_fires_on_k9_plus(self, tmp_path):
        _write_minimal(
            tmp_path, grade=9, id="k9_easy_addition_01",
            topic="arithmetic.addition",
        )
        findings = lint_path(tmp_path)
        track = [f for f in findings if f.rule == "track_missing"]
        assert len(track) == 1
        assert track[0].severity == "info"

    def test_track_missing_lint_silent_when_set(self, tmp_path):
        _write_minimal(
            tmp_path, grade=12, id="k12_easy_addition_01",
            topic="arithmetic.addition", track="tertiary",
        )
        findings = lint_path(tmp_path)
        track = [f for f in findings if f.rule == "track_missing"]
        assert track == []


# ---------------------------------------------------------------------------
# B3/B4 — TestCase compare/tolerance and compare_answers helper
# ---------------------------------------------------------------------------

class TestB3B4CompareAnswers:
    """Unit tests for the comparison helper. Behavioural — covers each
    mode plus the malformed-input fallbacks."""

    def test_string_default_exact(self):
        assert compare_answers("5", "5")
        assert not compare_answers("5", "6")

    def test_string_explicit_mode(self):
        assert compare_answers("hi", "hi", mode="string")

    def test_numeric_strict_equality(self):
        assert compare_answers("5.0", "5.0", mode="numeric")
        assert not compare_answers("5.1", "5.0", mode="numeric")

    def test_numeric_absolute_tolerance(self):
        assert compare_answers("5.005", "5.0", mode="numeric", tolerance=0.01)
        assert not compare_answers("5.05", "5.0", mode="numeric", tolerance=0.01)

    def test_numeric_relative_tolerance(self):
        # 5% relative on 10000 → 500 absolute slack
        assert compare_answers("10500", "10000", mode="numeric", tolerance_rel=0.05)
        assert not compare_answers("11000", "10000", mode="numeric", tolerance_rel=0.05)

    def test_numeric_or_combination(self):
        # absolute fails, relative passes → OR makes it pass
        assert compare_answers(
            "10500", "10000", mode="numeric",
            tolerance=10.0, tolerance_rel=0.1,
        )

    def test_numeric_zero_denominator_handles_gracefully(self):
        assert compare_answers("0", "0", mode="numeric", tolerance_rel=0.1)
        assert not compare_answers("0.5", "0", mode="numeric", tolerance_rel=0.1)

    def test_numeric_parse_failure_falls_back_to_string(self):
        # Both unparseable but identical → string fallback returns True.
        assert compare_answers("oops", "oops", mode="numeric")
        assert not compare_answers("oops", "uh-oh", mode="numeric")

    def test_symbolic_double_angle(self):
        assert compare_answers("2*sin(x)*cos(x)", "sin(2*x)", mode="symbolic")

    def test_symbolic_polynomial_expansion(self):
        assert compare_answers(
            "(a+b)**2", "a**2 + 2*a*b + b**2", mode="symbolic",
        )

    def test_symbolic_inequality(self):
        assert not compare_answers("x + 1", "x - 1", mode="symbolic")

    def test_symbolic_parse_failure_falls_back_to_string(self):
        assert compare_answers("not parseable !@#", "not parseable !@#", mode="symbolic")

    def test_invalid_mode_raises(self):
        with pytest.raises(ValueError, match="Invalid compare mode"):
            compare_answers("1", "1", mode="bogus")


class TestB3B4Schema:
    """TestCase schema validation for the new fields."""

    def _write_test_block(self, tmp_path, tests):
        path = _write_minimal(tmp_path)
        # Rewrite tests by editing the YAML directly.
        data = yaml.safe_load(path.read_text())
        data["tests"] = tests
        path.write_text(yaml.safe_dump(data, sort_keys=False))
        return path

    def test_compare_string_loads(self, tmp_path):
        path = self._write_test_block(tmp_path, [
            {"seed": 1, "expected": {"answer": "2"}, "compare": "string"},
        ])
        loader = YAMLLoader()
        tpl = loader.load_template(path)
        assert tpl is not None, loader.errors
        assert tpl.tests[0].compare == "string"

    def test_compare_numeric_with_tolerance(self, tmp_path):
        path = self._write_test_block(tmp_path, [
            {
                "seed": 1, "expected": {"answer": "2"},
                "compare": "numeric", "tolerance": 0.5,
                "tolerance_rel": 0.01,
            },
        ])
        loader = YAMLLoader()
        tpl = loader.load_template(path)
        assert tpl is not None, loader.errors
        tc = tpl.tests[0]
        assert tc.compare == "numeric"
        assert tc.tolerance == 0.5
        assert tc.tolerance_rel == 0.01

    def test_invalid_compare_rejected(self, tmp_path):
        path = self._write_test_block(tmp_path, [
            {"seed": 1, "expected": {"answer": "2"}, "compare": "fuzzy"},
        ])
        loader = YAMLLoader()
        tpl = loader.load_template(path)
        assert tpl is None
        assert any("compare" in e for e in loader.errors)

    def test_negative_tolerance_rejected(self, tmp_path):
        path = self._write_test_block(tmp_path, [
            {
                "seed": 1, "expected": {"answer": "2"},
                "compare": "numeric", "tolerance": -0.1,
            },
        ])
        loader = YAMLLoader()
        tpl = loader.load_template(path)
        assert tpl is None
        assert any("tolerance" in e for e in loader.errors)

    def test_tolerance_with_string_mode_warns(self, tmp_path):
        path = self._write_test_block(tmp_path, [
            {
                "seed": 1, "expected": {"answer": "2"},
                "compare": "string", "tolerance": 0.1,
            },
        ])
        loader = YAMLLoader()
        loader.load_template(path)
        assert any("tolerance" in w for w in loader.warnings)


# ---------------------------------------------------------------------------
# B1 — symbolic answer dispatch in format_answer
# ---------------------------------------------------------------------------

class TestB1SymbolicFormatting:
    """Sympy / Matrix / complex Answers route through the new helpers
    before any numeric branch sees them. Existing numeric / unit-aware
    paths must remain byte-identical (verified by full pytest +
    mathbot lint elsewhere)."""

    def test_pure_numeric_sympy_falls_through_to_decimal(self):
        # sqrt(2) is_number → coerced to float → decimal branch wins.
        spec = VariableSpec(name="Answer", type="decimal")
        out = format_answer(sp.sqrt(2), spec)
        assert out == "1.41"

    def test_pure_numeric_sympy_falls_through_to_integer(self):
        spec = VariableSpec(name="Answer", type="integer")
        out = format_answer(sp.Integer(42), spec)
        assert out == "42"

    def test_symbolic_simplifies(self):
        x = sp.symbols("x")
        spec = VariableSpec(name="Answer", type="string")
        out = format_answer(2 * sp.sin(x) * sp.cos(x), spec)
        assert out == "sin(2*x)"

    def test_symbolic_with_unit_appends_pint_pretty(self):
        # Symbolic + free-form unit should emit a pretty pint suffix.
        omega, t = sp.symbols("omega t")
        spec = VariableSpec(name="Answer", type="length", unit="meter")
        out = format_answer(3 * sp.cos(omega * t), spec)
        assert "cos(omega*t)" in out
        assert out.endswith(" m")

    def test_matrix_integer(self):
        spec = VariableSpec(name="Answer", type="string")
        out = format_answer(sp.Matrix([[1, 2], [3, 4]]), spec)
        assert out == "[[1, 2], [3, 4]]"

    def test_matrix_symbolic(self):
        x = sp.symbols("x")
        spec = VariableSpec(name="Answer", type="string")
        rotation = sp.Matrix([[sp.cos(x), -sp.sin(x)], [sp.sin(x), sp.cos(x)]])
        out = format_answer(rotation, spec)
        assert out == "[[cos(x), -sin(x)], [sin(x), cos(x)]]"

    def test_complex_full(self):
        spec = VariableSpec(name="Answer", type="string")
        assert format_answer(complex(2, 3), spec) == "2 + 3i"
        assert format_answer(complex(2, -3), spec) == "2 - 3i"

    def test_complex_pure_real(self):
        spec = VariableSpec(name="Answer", type="string")
        assert format_answer(complex(5, 0), spec) == "5"

    def test_complex_pure_imag(self):
        spec = VariableSpec(name="Answer", type="string")
        assert format_answer(complex(0, 5), spec) == "5i"

    def test_complex_decimal_parts(self):
        spec = VariableSpec(name="Answer", type="string")
        assert format_answer(complex(1.5, 2.5), spec) == "1.50 + 2.50i"

    def test_legacy_float_path_unchanged(self):
        # A regular float must still pick up the type-specific dispatch
        # (i.e. NOT be intercepted by the symbolic branch) — guards the
        # byte-identity of the existing 1278-fixture corpus.
        spec = VariableSpec(name="Answer", type="money", unit_system="mixed_us")
        assert format_answer(12.5, spec) == "$12.50"

    def test_integer_path_unchanged(self):
        spec = VariableSpec(name="Answer", type="integer")
        assert format_answer(7, spec) == "7"
