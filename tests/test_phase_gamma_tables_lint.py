"""Phase γ.3 tests — TableSVG (A.1) + lint rules (A.4).

Workstream A.1 ships the table builder with four output methods
(to_svg / to_text / to_markdown / to_latex) plus three named
variants (FunctionValueTable, MatrixTable, DataTable).

Workstream A.4 ships five lint rules:

- ``simplification_lift_missing`` — multi-tier templates whose
  ``simplifications:`` entries don't actually vary by tier.
- ``feature_declared_but_unused`` — declared schema features (today:
  ``simplifications:``) without fixtures exercising them.
- ``figure_load_inconsistent`` — prose ↔ figure_load mismatch.
- ``visual_prose_contradiction`` — alt-text / prose token-overlap.
- ``axis_range_artifact`` — visual SVG carries un-round axis labels.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
import yaml

from src.audit import lint_path
from src.audit.findings import Finding
from src.audit.lint import (
    _is_axis_label_artifact,
    check_axis_range_artifact,
    check_feature_declared_but_unused,
    check_figure_load_inconsistent,
    check_simplification_lift_missing,
    check_visual_prose_contradiction,
)
from src.audit.render import RenderedSample
from src.visuals import (
    DataTable,
    FunctionValueTable,
    MatrixTable,
    TableSVG,
)
from src.yaml_loader import (
    SimplificationSpec,
    TemplateDefinition,
    VariableSpec,
    VisualSpec,
    YAMLLoader,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_template(
    tmp_path: Path,
    *,
    metadata_overrides=None,
    body: str = "{{a}} + {{b}} = ?",
    solution: str = "Answer = a + b",
    variables=None,
    visual=None,
    expected_answer: str = "3",
    test_difficulty=None,
):
    topic_dir = tmp_path / "arithmetic"
    topic_dir.mkdir(parents=True, exist_ok=True)
    metadata = {
        "id": "k9_easy_addition_smoke",
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
    if visual is not None:
        payload["visual"] = visual
    path = topic_dir / f"{metadata['id']}.yaml"
    path.write_text(yaml.safe_dump(payload, sort_keys=False))
    return path


def _make_template(**overrides) -> TemplateDefinition:
    """Construct a TemplateDefinition fixture inline (no YAML round-trip)."""
    base = dict(
        id="k12_test_01",
        version="1.0.0",
        author="t",
        created="2026-04-29",
        grade=12,
        topic="calculus.optimization",
        family="derivative_application",
        difficulty="medium",
        steps=4,
    )
    base.update(overrides)
    return TemplateDefinition(**base)


def _sample(body: str, tier: str = "easy", seed: int = 1) -> RenderedSample:
    return RenderedSample(
        template_id="t",
        seed=seed, tier=tier,
        body=body, answer="0",
        raw={},
    )


# ---------------------------------------------------------------------------
# A.1 — TableSVG
# ---------------------------------------------------------------------------

class TestTableSVGCore:
    def test_to_svg_parses_as_xml(self):
        t = TableSVG(headers=["x", "f(x)"], rows=[[0, 1], [1, 4]])
        root = ET.fromstring(t.to_svg())
        assert root.tag.endswith("svg")
        # Headers + 4 cells = 6 text nodes minimum
        texts = root.findall(".//{http://www.w3.org/2000/svg}text")
        assert len(texts) >= 6

    def test_render_returns_svg(self):
        t = TableSVG(headers=["a", "b"], rows=[[1, 2]])
        # Visual sandbox contract — render() = to_svg()
        assert t.render() == t.to_svg()

    def test_to_text_box_drawing(self):
        t = TableSVG(headers=["x", "f(x)"], rows=[[0, 1], [1, 4]])
        out = t.to_text()
        # Top + middle + bottom borders use box-drawing chars
        assert "┌" in out and "┐" in out
        assert "└" in out and "┘" in out
        assert "┼" in out
        assert "│ x" in out
        assert "│ 1 " in out

    def test_to_markdown_pipe_table(self):
        t = TableSVG(headers=["x", "f(x)"], rows=[[0, 1], [1, 4]])
        out = t.to_markdown()
        # Header row + alignment row + 2 data rows
        assert out.count("| x |") == 1
        assert "| ---: |" in out  # right-aligned numeric
        assert "| 0 | 1 |" in out

    def test_to_latex_tabular(self):
        t = TableSVG(headers=["x", "f(x)"], rows=[[0, 1], [1, 4]])
        out = t.to_latex()
        assert r"\begin{tabular}" in out
        assert r"\end{tabular}" in out
        assert r"\hline" in out
        # Both columns numeric → both 'r' alignment
        assert "{|r|r|}" in out

    def test_caption_in_text_markdown_latex(self):
        t = TableSVG(
            headers=["x", "y"], rows=[[1, 2]],
            caption="Sample function",
        )
        assert "Sample function" in t.to_text().splitlines()[0]
        assert "*Sample function*" in t.to_markdown()
        assert r"\caption*{Sample function}" in t.to_latex()

    def test_highlight_cells_emit_rect(self):
        t = TableSVG(
            headers=["a", "b"], rows=[[1, 2], [3, 4]],
            highlights=[(0, 1)],
        )
        svg = t.to_svg()
        # Highlight tint
        assert "#fff7c2" in svg

    def test_highlight_outside_grid_silently_ignored(self):
        t = TableSVG(
            headers=["a"], rows=[[1]],
            highlights=[(99, 99)],
        )
        # Out-of-range coords are ignored; SVG still renders cleanly.
        svg = t.to_svg()
        assert "#fff7c2" not in svg

    def test_uneven_row_rejected(self):
        with pytest.raises(ValueError, match="row 0"):
            TableSVG(headers=["x", "y"], rows=[[1]])

    def test_invalid_align_rejected(self):
        with pytest.raises(ValueError, match="align entry"):
            TableSVG(headers=["x"], rows=[[1]], align=["sideways"])

    def test_align_length_mismatch_rejected(self):
        with pytest.raises(ValueError, match="align: expected"):
            TableSVG(headers=["x", "y"], rows=[[1, 2]], align=["left"])

    def test_numeric_columns_right_align_by_default(self):
        t = TableSVG(headers=["x", "label"], rows=[[1.5, "alpha"]])
        # Column 0 numeric → right; column 1 string → left.
        assert t.align == ["right", "left"]

    def test_pipe_in_cell_escaped_for_markdown(self):
        t = TableSVG(headers=["x", "y"], rows=[["a|b", "c"]])
        md = t.to_markdown()
        assert r"a\|b" in md

    def test_special_chars_escaped_for_latex(self):
        t = TableSVG(headers=["price"], rows=[["$1.50"]])
        tex = t.to_latex()
        assert r"\$1.50" in tex


class TestFunctionValueTable:
    def test_two_columns_with_default_labels(self):
        t = FunctionValueTable([0, 1, 2], [1, 4, 9])
        assert t.headers == ["x", "f(x)"]
        assert t.rows == [["0", "1"], ["1", "4"], ["2", "9"]]

    def test_custom_labels(self):
        t = FunctionValueTable(
            [0, 1], [1, 4],
            x_label="x_i", y_label="f(x_i)",
        )
        assert t.headers == ["x_i", "f(x_i)"]

    def test_highlight_indices_target_y_column(self):
        t = FunctionValueTable(
            [0, 1, 2], [1, 4, 9],
            highlight_indices=[0, 2],
        )
        # Each index → (row, col=1)
        assert (0, 1) in t.highlights
        assert (2, 1) in t.highlights

    def test_length_mismatch_rejected(self):
        with pytest.raises(ValueError, match="must have the same length"):
            FunctionValueTable([0, 1], [1, 4, 9])


class TestMatrixTable:
    def test_sympy_matrix(self):
        import sympy as sp
        m = sp.Matrix([[1, 2], [3, 4]])
        t = MatrixTable(m)
        assert len(t.rows) == 2
        assert t.rows[0] == ["1", "2"]
        assert t.rows[1] == ["3", "4"]

    def test_row_and_col_labels(self):
        t = MatrixTable(
            [[1, 2], [3, 4]],
            row_labels=["r1", "r2"],
            col_labels=["c1", "c2"],
        )
        # Empty corner + col labels
        assert t.headers == ["", "c1", "c2"]
        # Row label prefix
        assert t.rows[0][0] == "r1"

    def test_centered_alignment_by_default(self):
        t = MatrixTable([[1, 2], [3, 4]])
        assert all(a == "center" for a in t.align)

    def test_empty_matrix_rejected(self):
        with pytest.raises(ValueError, match="at least one row"):
            MatrixTable([])

    def test_col_label_length_mismatch_rejected(self):
        with pytest.raises(ValueError, match="col_labels: expected"):
            MatrixTable([[1, 2]], col_labels=["only_one"])


class TestDataTable:
    def test_alias_for_table_svg(self):
        t = DataTable(headers=["a", "b"], rows=[[1, 2]])
        assert isinstance(t, TableSVG)


# ---------------------------------------------------------------------------
# A.4 — lint rules (unit-level)
# ---------------------------------------------------------------------------

class TestAxisRangeArtifact:
    # γ.4q restricts the rule to plot-shaped SVGs (presence of
    # `<polyline>`); table SVGs no longer false-positive on integer
    # cell values. Tests now include the polyline marker.

    def test_clean_round_labels_ok(self):
        svg = '<svg><polyline/><text>0</text><text>5</text><text>10</text></svg>'
        assert check_axis_range_artifact(svg, _make_template()) == []

    def test_one_decimal_ok(self):
        svg = '<svg><polyline/><text>1.5</text><text>0.5</text></svg>'
        assert check_axis_range_artifact(svg, _make_template()) == []

    def test_trailing_zero_stripped(self):
        # "1.50" reads as "1.5" after trim → not artifact
        svg = '<svg><polyline/><text>1.50</text><text>2.00</text></svg>'
        assert check_axis_range_artifact(svg, _make_template()) == []

    def test_two_decimal_artifact_fires(self):
        svg = '<svg><polyline/><text>37.85</text></svg>'
        f = check_axis_range_artifact(svg, _make_template())
        assert len(f) == 1
        assert f[0].rule == "axis_range_artifact"
        assert f[0].severity == "warning"
        assert "37.85" in f[0].message

    def test_no_polyline_no_finding(self):
        # Table-shaped SVGs (no <polyline>) skip the rule entirely
        # so integer table cells don't false-positive.
        svg = '<svg><rect/><text>17</text><text>37.85</text></svg>'
        assert check_axis_range_artifact(svg, _make_template()) == []

    def test_no_visual_no_finding(self):
        assert check_axis_range_artifact("", _make_template()) == []

    def test_helper_unit(self):
        assert _is_axis_label_artifact("1.5") is False
        assert _is_axis_label_artifact("1.50") is False
        assert _is_axis_label_artifact("37.85") is True
        assert _is_axis_label_artifact("3.14159") is True
        assert _is_axis_label_artifact("100") is False


class TestSimplificationLiftMissing:
    def test_no_simplifications_no_finding(self):
        t = _make_template(difficulty_tiers=["easy", "medium", "hard"])
        assert check_simplification_lift_missing(t) == []

    def test_single_tier_no_finding(self):
        t = _make_template(simplifications=[
            SimplificationSpec(text="X", omit_at=[]),
        ])
        # difficulty_tiers is None
        assert check_simplification_lift_missing(t) == []

    def test_all_omit_at_identical_fires(self):
        t = _make_template(
            difficulty_tiers=["easy", "medium", "hard"],
            simplifications=[
                SimplificationSpec(text="A", omit_at=[]),
                SimplificationSpec(text="B", omit_at=[]),
            ],
        )
        f = check_simplification_lift_missing(t)
        assert len(f) == 1
        assert f[0].rule == "simplification_lift_missing"
        assert f[0].severity == "warning"

    def test_varying_omit_at_no_finding(self):
        t = _make_template(
            difficulty_tiers=["easy", "medium", "hard"],
            simplifications=[
                SimplificationSpec(text="A", omit_at=["hard"]),
                SimplificationSpec(text="B", omit_at=[]),
            ],
        )
        assert check_simplification_lift_missing(t) == []


class TestFigureLoadInconsistent:
    def test_no_figure_load_no_finding(self):
        t = _make_template()
        s = _sample("solve for x.")
        assert check_figure_load_inconsistent(s, t) == []

    def test_prose_references_figure_with_no_visual(self):
        t = _make_template()
        s = _sample("As shown in the figure below, find x.")
        f = check_figure_load_inconsistent(s, t)
        assert len(f) == 1
        assert "no `visual:` block" in f[0].message

    def test_decorative_load_with_figure_phrase(self):
        t = _make_template(
            visual=VisualSpec(format="svg", source="<svg/>"),
            figure_load="decorative",
        )
        s = _sample("As shown in the figure, compute the area.")
        f = check_figure_load_inconsistent(s, t)
        assert len(f) == 1
        assert "decorative" in f[0].message

    def test_load_bearing_with_figure_phrase_no_finding(self):
        t = _make_template(
            visual=VisualSpec(format="svg", source="<svg/>"),
            figure_load="load_bearing",
        )
        s = _sample("As shown in the figure, compute the area.")
        assert check_figure_load_inconsistent(s, t) == []

    def test_per_tier_mapping(self):
        t = _make_template(
            visual=VisualSpec(format="svg", source="<svg/>"),
            figure_load={"easy": "decorative", "hard": "load_bearing"},
            difficulty_tiers=["easy", "medium", "hard"],
        )
        s_easy = _sample("As shown in the figure", tier="easy")
        s_hard = _sample("As shown in the figure", tier="hard")
        # easy → decorative + figure phrase → fire
        assert len(check_figure_load_inconsistent(s_easy, t)) == 1
        # hard → load_bearing + figure phrase → no finding
        assert check_figure_load_inconsistent(s_hard, t) == []


class TestFeatureDeclaredButUnused:
    def test_no_simplifications_no_finding(self):
        t = _make_template()
        assert check_feature_declared_but_unused(t) == []

    def test_simplifications_without_multi_tier_no_finding(self):
        t = _make_template(simplifications=[
            SimplificationSpec(text="X", omit_at=[]),
        ])
        # Single-tier; no fixtures-per-tier check applies
        assert check_feature_declared_but_unused(t) == []

    def test_multi_tier_with_partial_fixtures_fires(self):
        from src.yaml_loader import TestCase
        t = _make_template(
            difficulty_tiers=["easy", "medium", "hard"],
            simplifications=[
                SimplificationSpec(text="A", omit_at=["hard"]),
            ],
            tests=[
                TestCase(seed=1, expected={"answer": "1"}, difficulty="easy"),
            ],
        )
        f = check_feature_declared_but_unused(t)
        assert len(f) == 1
        assert "medium" in f[0].message
        assert "hard" in f[0].message

    def test_multi_tier_with_full_fixtures_no_finding(self):
        from src.yaml_loader import TestCase
        t = _make_template(
            difficulty_tiers=["easy", "medium", "hard"],
            simplifications=[
                SimplificationSpec(text="A", omit_at=["hard"]),
            ],
            tests=[
                TestCase(seed=1, expected={"answer": "1"}, difficulty="easy"),
                TestCase(seed=2, expected={"answer": "1"}, difficulty="medium"),
                TestCase(seed=3, expected={"answer": "1"}, difficulty="hard"),
            ],
        )
        assert check_feature_declared_but_unused(t) == []


class TestVisualProseContradiction:
    def test_no_visual_no_finding(self):
        t = _make_template()
        s = _sample("solve for x.")
        assert check_visual_prose_contradiction(s, t) == []

    def test_no_alt_text_no_finding(self):
        t = _make_template(
            visual=VisualSpec(format="svg", source="<svg/>", alt_text=""),
        )
        s = _sample("solve for x.")
        assert check_visual_prose_contradiction(s, t) == []

    def test_overlap_no_finding(self):
        t = _make_template(
            visual=VisualSpec(
                format="svg", source="<svg/>",
                alt_text="A circle inscribed in a square.",
            ),
        )
        s = _sample("Compute the area of the circle.")
        assert check_visual_prose_contradiction(s, t) == []

    def test_no_overlap_fires(self):
        t = _make_template(
            visual=VisualSpec(
                format="svg", source="<svg/>",
                alt_text="A spiral pattern winding around the origin.",
            ),
        )
        s = _sample("Compute the area of the rectangle.")
        f = check_visual_prose_contradiction(s, t)
        assert len(f) == 1
        assert f[0].severity == "info"


# ---------------------------------------------------------------------------
# Integration: rules are wired into lint_path
# ---------------------------------------------------------------------------

class TestRulesIntegrated:
    def test_simplification_lift_missing_wired(self, tmp_path):
        path = _write_template(
            tmp_path,
            metadata_overrides={
                "difficulty_tiers": ["easy", "medium", "hard"],
                "simplifications": [
                    {"text": "A", "omit_at": []},
                    {"text": "B", "omit_at": []},
                ],
            },
        )
        findings = lint_path(path)
        assert any(f.rule == "simplification_lift_missing" for f in findings)

    def test_figure_load_inconsistent_wired(self, tmp_path):
        path = _write_template(
            tmp_path,
            body="As shown in the figure below, what is {{a}} + {{b}}?",
            metadata_overrides={"figure_load": "decorative"},
            visual={
                "format": "svg",
                "source": '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"><rect width="10" height="10"/></svg>',
                "alt_text": "decorative graphic",
            },
        )
        findings = lint_path(path)
        assert any(f.rule == "figure_load_inconsistent" for f in findings)

    def test_clean_template_no_new_findings(self, tmp_path):
        # A template that doesn't trigger any γ.3 rules.
        path = _write_template(tmp_path)
        findings = lint_path(path)
        new_rules = {
            "axis_range_artifact",
            "simplification_lift_missing",
            "figure_load_inconsistent",
            "feature_declared_but_unused",
            "visual_prose_contradiction",
        }
        assert not any(f.rule in new_rules for f in findings)
