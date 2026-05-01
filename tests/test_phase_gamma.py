"""Phase γ.1 foundation tests.

Covers the schema additions in workstream A.3 plus the B.5 ``MathExpr``
keystone:

- A.3: ``simplifications:`` list with per-tier ``omit_at`` filtering;
  ``figure_load:`` (string or per-tier mapping); ``T18_assumption_omission``
  in the structural-tags enum.
- B.5: ``MathExpr.to_text`` (single-line Unicode), ``to_latex`` (raw
  LaTeX, no ``$``), ``to_markdown`` (``$<latex>$``); SVG/PNG paths
  raise ``NotImplementedError`` until KaTeX integration lands.

The deprecation path for ``noop_clauses`` is exercised here at the
schema level (still loads) — the lint info-finding lands in γ.3.
"""

from pathlib import Path

import pytest
import sympy as sp
import yaml

from src.render import MathExpr
from src.template_generator import TemplateGenerator
from src.yaml_loader import (
    SimplificationSpec,
    TemplateDefinition,
    YAMLLoader,
)


# ---------------------------------------------------------------------------
# Helpers (mirrors test_phase_beta._write_template style)
# ---------------------------------------------------------------------------

def _write_template(
    tmp_path: Path,
    *,
    metadata_overrides=None,
    body: str = "{{a}} + {{b}} = ?",
    solution: str = "Answer = a + b",
    expected_answer: str = "3",
    variables=None,
    test_difficulty=None,
):
    topic_dir = tmp_path / "arithmetic"
    topic_dir.mkdir(parents=True, exist_ok=True)
    metadata = {
        "id": "k9_easy_addition_01",
        "version": "1.0.0",
        "author": "t",
        "created": "2026-04-29",
        "grade": 9,
        "topic": "arithmetic.addition",
        "family": "addition",
        "difficulty": "easy",
        "steps": 1,
    }
    if metadata_overrides:
        metadata.update(metadata_overrides)
    test_entry = {"seed": 1, "expected": {"answer": expected_answer}}
    if test_difficulty:
        test_entry["difficulty"] = test_difficulty
    payload = {
        "metadata": metadata,
        "variables": variables or {
            "a": {"type": "integer", "min": 1, "max": 1},
            "b": {"type": "integer", "min": 2, "max": 2},
            "Answer": {"type": "integer"},
        },
        "template": body,
        "solution": solution,
        "tests": [test_entry],
    }
    path = topic_dir / f"{metadata['id']}.yaml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False))
    return path


# ---------------------------------------------------------------------------
# A.3 — simplifications
# ---------------------------------------------------------------------------

class TestA3Simplifications:
    def test_default_empty(self, tmp_path):
        path = _write_template(tmp_path)
        tpl = YAMLLoader().load_template(path)
        assert tpl is not None
        assert tpl.simplifications == []

    def test_loaded_as_dataclass(self, tmp_path):
        path = _write_template(tmp_path, metadata_overrides={
            "simplifications": [
                {"text": "Treat the cup as a perfect cone.", "omit_at": ["hard"]},
                {"text": "The lid is open."},  # no omit_at → always present
            ],
        })
        tpl = YAMLLoader().load_template(path)
        assert tpl is not None
        assert len(tpl.simplifications) == 2
        assert isinstance(tpl.simplifications[0], SimplificationSpec)
        assert tpl.simplifications[0].omit_at == ["hard"]
        assert tpl.simplifications[1].omit_at == []

    def test_invalid_omit_tier_rejected(self, tmp_path):
        path = _write_template(tmp_path, metadata_overrides={
            "simplifications": [
                {"text": "x", "omit_at": ["sideways"]},
            ],
        })
        loader = YAMLLoader()
        tpl = loader.load_template(path)
        assert tpl is None
        assert any("simplifications" in e for e in loader.errors)

    def test_missing_text_rejected(self, tmp_path):
        path = _write_template(tmp_path, metadata_overrides={
            "simplifications": [{"omit_at": []}],
        })
        loader = YAMLLoader()
        tpl = loader.load_template(path)
        assert tpl is None
        assert any("text" in e for e in loader.errors)

    def test_non_list_rejected(self, tmp_path):
        path = _write_template(tmp_path, metadata_overrides={
            "simplifications": "single string"
        })
        loader = YAMLLoader()
        tpl = loader.load_template(path)
        assert tpl is None

    def test_jinja_renders_at_active_tier(self, tmp_path):
        # Multi-tier template: simplification active at easy/medium,
        # suppressed at hard.
        path = _write_template(
            tmp_path,
            body="{{ simplifications }} What is {{a}} + {{b}}?",
            metadata_overrides={
                "difficulty": "easy",
                "difficulty_tiers": ["easy", "medium", "hard"],
                "simplifications": [
                    {"text": "Assume {{a}} is constant.", "omit_at": ["hard"]},
                ],
            },
            variables={
                "a": {"type": "integer", "min": 5, "max": 5},
                "b": {"type": "integer", "min": 7, "max": 7},
                "Answer": {"type": "integer"},
            },
            expected_answer="12",
            test_difficulty="easy",
        )
        gen = TemplateGenerator(templates_dir=tmp_path, seed=1)
        # easy tier: simplification surfaces
        prob_easy = gen.generate(complexity=1, seed=1)
        assert "Assume 5 is constant." in prob_easy["problem"]
        # hard tier: simplification suppressed
        prob_hard = gen.generate(complexity=3, seed=1)
        assert "Assume" not in prob_hard["problem"]

    def test_default_empty_string_when_unused(self, tmp_path):
        # No `simplifications:` set → `{{ simplifications }}` is "".
        path = _write_template(
            tmp_path,
            body="{{ simplifications }}{{a}} + {{b}} = ?",
        )
        gen = TemplateGenerator(templates_dir=tmp_path, seed=1)
        prob = gen.generate(seed=1)
        # Empty string substituted, no leading whitespace residue.
        assert prob["problem"].startswith("1 + 2")


# ---------------------------------------------------------------------------
# A.3 — figure_load
# ---------------------------------------------------------------------------

class TestA3FigureLoad:
    @pytest.mark.parametrize("value", ["none", "decorative", "partial", "load_bearing"])
    def test_valid_string_value(self, tmp_path, value):
        path = _write_template(tmp_path, metadata_overrides={"figure_load": value})
        loader = YAMLLoader()
        tpl = loader.load_template(path)
        assert tpl is not None, loader.errors
        assert tpl.figure_load == value

    def test_per_tier_mapping(self, tmp_path):
        path = _write_template(tmp_path, metadata_overrides={
            "figure_load": {
                "easy": "decorative",
                "medium": "partial",
                "hard": "load_bearing",
            },
        })
        loader = YAMLLoader()
        tpl = loader.load_template(path)
        assert tpl is not None, loader.errors
        assert tpl.figure_load == {
            "easy": "decorative",
            "medium": "partial",
            "hard": "load_bearing",
        }

    def test_default_none(self, tmp_path):
        path = _write_template(tmp_path)
        tpl = YAMLLoader().load_template(path)
        assert tpl.figure_load is None

    def test_invalid_value_rejected(self, tmp_path):
        path = _write_template(tmp_path, metadata_overrides={"figure_load": "important"})
        loader = YAMLLoader()
        tpl = loader.load_template(path)
        assert tpl is None
        assert any("figure_load" in e for e in loader.errors)

    def test_invalid_tier_key_rejected(self, tmp_path):
        path = _write_template(tmp_path, metadata_overrides={
            "figure_load": {"sideways": "decorative"},
        })
        loader = YAMLLoader()
        tpl = loader.load_template(path)
        assert tpl is None

    def test_non_string_non_dict_rejected(self, tmp_path):
        path = _write_template(tmp_path, metadata_overrides={"figure_load": 7})
        loader = YAMLLoader()
        tpl = loader.load_template(path)
        assert tpl is None


# ---------------------------------------------------------------------------
# A.3 — T18 structural tag
# ---------------------------------------------------------------------------

class TestA3T18Tag:
    def test_t18_in_valid_tags(self):
        assert "T18_assumption_omission" in YAMLLoader.VALID_STRUCTURAL_TAGS

    def test_t18_loads(self, tmp_path):
        path = _write_template(tmp_path, metadata_overrides={
            "structural_tags": ["T18_assumption_omission"],
        })
        tpl = YAMLLoader().load_template(path)
        assert tpl is not None
        assert "T18_assumption_omission" in tpl.structural_tags


# ---------------------------------------------------------------------------
# A.3 — noop_clauses still loads (deprecated, lint info finding lands in γ.3)
# ---------------------------------------------------------------------------

class TestA3NoopClausesStillLoads:
    def test_noop_clauses_still_loads(self, tmp_path):
        # The field is deprecated but the back-compat path stays through
        # the 0.6.x cycle. Removal lands in γ.5.
        path = _write_template(
            tmp_path,
            body="{{ noop_clause }} {{a}} + {{b}} = ?",
            metadata_overrides={
                "noop_clauses": ["Earlier in the day, {{a}} was popular."],
            },
        )
        tpl = YAMLLoader().load_template(path)
        assert tpl is not None
        assert tpl.noop_clauses == ["Earlier in the day, {{a}} was popular."]


# ---------------------------------------------------------------------------
# B.5 — MathExpr keystone
# ---------------------------------------------------------------------------

class TestB5MathExprText:
    def test_simple_power(self):
        assert MathExpr("x**2 + 1").to_text() == "x² + 1"

    def test_multidigit_power(self):
        assert MathExpr("y**12").to_text() == "y¹²"

    def test_negative_power(self):
        # Order varies by sympy normalisation; check both orderings.
        out = MathExpr("x**(-3) + 1").to_text()
        assert "x⁻³" in out

    def test_infinity_token(self):
        assert MathExpr(sp.oo).to_text() == "∞"

    def test_inequality_unicode(self):
        x = sp.Symbol("x")
        assert MathExpr(x <= 5).to_text() == "x ≤ 5"
        assert MathExpr(x >= 5).to_text() == "x ≥ 5"

    def test_equality_uses_infix(self):
        x = sp.Symbol("x")
        assert MathExpr(sp.Eq(x ** 2, 4)).to_text() == "x² = 4"

    def test_matrix_bracket_form(self):
        m = sp.Matrix([[1, 2], [3, 4]])
        assert MathExpr(m).to_text() == "[[1, 2], [3, 4]]"

    def test_matrix_with_expressions(self):
        a = sp.Symbol("a")
        m = sp.Matrix([[a ** 2, 1], [3, sp.oo]])
        assert MathExpr(m).to_text() == "[[a², 1], [3, ∞]]"

    def test_complex_number(self):
        # Real and imaginary parts present; Unicode i marker.
        out = MathExpr(2 + 3j).to_text()
        assert "2.0" in out
        assert "3.0" in out
        # sympy renders i as ⅈ in sstr Unicode form
        assert "ⅈ" in out or "I" in out

    def test_string_unparseable_passthrough(self):
        # Free-form string the formatter can't sympify falls through.
        assert MathExpr("3 hours 25 minutes").to_text() == "3 hours 25 minutes"

    def test_empty_string(self):
        assert MathExpr("").to_text() == ""

    def test_none_passthrough(self):
        assert MathExpr(None).to_text() == "None"

    def test_bool_not_coerced_to_int(self):
        # bool is an int subclass — the keystone must NOT render `True`
        # as `1`. Otherwise a boolean field in a template would print
        # the wrong glyph.
        assert MathExpr(True).to_text() == "True"
        assert MathExpr(False).to_text() == "False"


class TestB5MathExprLatex:
    def test_simple_power(self):
        assert MathExpr("x**2 + 1").to_latex() == "x^{2} + 1"

    def test_matrix(self):
        m = sp.Matrix([[1, 2], [3, 4]])
        out = MathExpr(m).to_latex()
        # sympy emits `\left[\begin{matrix}...` — check structural tokens
        assert r"\begin{matrix}" in out
        assert r"\end{matrix}" in out

    def test_latex_passthrough_for_strings(self):
        # Already a string the formatter can't parse → stays as-is.
        assert MathExpr("hello world").to_latex() == "hello world"

    def test_equality(self):
        x = sp.Symbol("x")
        assert MathExpr(sp.Eq(x ** 2, 4)).to_latex() == "x^{2} = 4"


class TestB5MathExprMarkdown:
    def test_wraps_in_dollars(self):
        assert MathExpr("x**2 + 1").to_markdown() == "$x^{2} + 1$"

    def test_passthrough_string_still_dollar_wrapped(self):
        # Even when sympify fails, markdown still wraps. Downstream
        # GH MathJax will render the raw text as italic — acceptable
        # softness; the alternative is detecting "is this LaTeX?" which
        # is ambiguous.
        assert MathExpr("hello").to_markdown() == "$hello$"


class TestB5MathExprStubs:
    def test_to_svg_raises(self):
        with pytest.raises(NotImplementedError, match="KaTeX"):
            MathExpr("x").to_svg()

    def test_to_png_raises(self):
        with pytest.raises(NotImplementedError, match="KaTeX"):
            MathExpr("x").to_png()


class TestB5MathExprFormPreservation:
    """Regression: parse_expr(evaluate=False) keeps the user's algebraic form.

    Reported during γ.2 review: at the same seed the markdown / latex
    pipelines printed the auto-distributed form (``(4t+4)*exp(-t)``)
    while the SVG composite used the formatter's factored form
    (``4*(t+1)*exp(-t)``). The fix routes string→sympy through
    ``parse_expr(evaluate=False)`` so the distribution doesn't fire
    during the round-trip. Lock it in.
    """

    def test_factored_form_round_trips(self):
        # Eager sympify auto-distributes 4*(t+1) → 4t+4. The keystone
        # must NOT do that.
        e = MathExpr("4*(t + 1)*exp(-t)")
        latex = e.to_latex()
        assert r"\left(t + 1\right)" in latex, latex
        assert "4 t + 4" not in latex
        assert "4*t + 4" not in latex

    def test_text_form_matches_input(self):
        # The text rendering of the canonical sstr form should produce
        # the same form (no `**N` to lift, no surprises).
        text = MathExpr("4*(t + 1)*exp(-t)").to_text()
        assert text == "4*(t + 1)*exp(-t)"

    def test_quadratic_factored_form_preserved(self):
        # `(x - 1)*(x + 1)` should stay factored, not expand to x²-1.
        latex = MathExpr("(x - 1)*(x + 1)").to_latex()
        assert r"\left(x - 1\right)" in latex
        assert r"\left(x + 1\right)" in latex


class TestB5MathExprDunder:
    def test_str_is_to_text(self):
        e = MathExpr("x**2")
        assert str(e) == e.to_text()

    def test_repr_round_trips(self):
        e = MathExpr("x**2 + 1")
        # repr keeps the raw input form so a reader can reconstruct
        assert "x**2 + 1" in repr(e)

    def test_equality_via_simplify(self):
        # Same algebraic expression, different surface form → equal.
        a = MathExpr("x**2 - 1")
        b = MathExpr("(x - 1)*(x + 1)")
        assert a == b

    def test_inequality_for_distinct_expressions(self):
        assert MathExpr("x + 1") != MathExpr("x + 2")
