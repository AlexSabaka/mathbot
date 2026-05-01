"""Phase γ.3 (A.2) tests — :class:`OptimizationRegionFigure`.

Coverage:

1. Canonical LP example (``x+y≤10, 2x+y≤14, x≥0, y≥0``) — vertices,
   axis frame, polygon presence.
2. Determinism: same args → byte-identical SVG.
3. ``to_text`` lists constraints + computed vertices.
4. ``to_latex`` emits a TikZ picture with a polygon when the region is
   non-empty; falls back to ``\\fbox{[Figure: ...]}`` when empty.
5. Equality constraint: line-segment region renders without crashing.
6. Empty feasible region: graceful handling — empty polygon + alt-text.
7. Objective gradient arrow: optional, draws when supplied.
8. Construction validation: bad ops, all-zero coefficients rejected.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from src.visuals.figures.optimization_region import OptimizationRegionFigure


# Canonical LP example used by several tests below. Feasible-region
# vertices on this LP are (0,0), (7,0), (4,6), (0,10).
CANONICAL_CONSTRAINTS = [
    (1, 1, "le", 10),
    (2, 1, "le", 14),
    (1, 0, "ge", 0),
    (0, 1, "ge", 0),
]


def _parse(svg: str) -> ET.Element:
    return ET.fromstring(svg)


class TestCanonicalLP:
    """Verify geometry + SVG structure on the canonical LP example."""

    def test_renders_polygon_with_correct_vertices(self):
        f = OptimizationRegionFigure(constraints=CANONICAL_CONSTRAINTS)
        assert len(f._vertices) == 4
        # Sort for comparison — the builder stores them CCW around centroid.
        verts = sorted(((round(x, 6), round(y, 6)) for x, y in f._vertices))
        assert verts == [(0.0, 0.0), (0.0, 10.0), (4.0, 6.0), (7.0, 0.0)]

    def test_svg_contains_polygon_element(self):
        f = OptimizationRegionFigure(constraints=CANONICAL_CONSTRAINTS)
        svg = f.to_svg()
        root = _parse(svg)
        ns = "{http://www.w3.org/2000/svg}"
        polys = root.findall(f".//{ns}polygon")
        assert len(polys) >= 1
        # Region polygon has the light fill specified in the spec.
        assert any(p.get("fill") == "#e0e7ff" for p in polys)

    def test_svg_has_integer_axis_tick_labels(self):
        f = OptimizationRegionFigure(constraints=CANONICAL_CONSTRAINTS)
        svg = f.to_svg()
        root = _parse(svg)
        ns = "{http://www.w3.org/2000/svg}"
        # Some integer ticks within the auto-fit range should land as
        # text labels — at least "0" and one positive value.
        texts = [t.text for t in root.findall(f".//{ns}text") if t.text]
        assert "0" in texts
        # Auto-fit pushes upper bound past 10, so at least one of these
        # ticks should be present.
        assert any(t in texts for t in ("4", "5", "6", "7", "8", "10"))


class TestDeterminism:
    def test_same_args_byte_identical(self):
        a = OptimizationRegionFigure(constraints=CANONICAL_CONSTRAINTS).to_svg()
        b = OptimizationRegionFigure(constraints=CANONICAL_CONSTRAINTS).to_svg()
        assert a == b


class TestToText:
    def test_lists_constraints_and_vertices(self):
        f = OptimizationRegionFigure(constraints=CANONICAL_CONSTRAINTS)
        txt = f.to_text()
        # Constraint forms.
        assert "x + y ≤ 10" in txt
        assert "2x + y ≤ 14" in txt
        assert "x ≥ 0" in txt
        assert "y ≥ 0" in txt
        # All four vertices listed (in some order).
        for vertex_str in ("(0,0)", "(7,0)", "(4,6)", "(0,10)"):
            assert vertex_str in txt


class TestToLatex:
    def test_contains_tikzpicture_when_feasible(self):
        f = OptimizationRegionFigure(constraints=CANONICAL_CONSTRAINTS)
        latex = f.to_latex()
        assert r"\begin{tikzpicture}" in latex
        assert r"\end{tikzpicture}" in latex
        # Should include a filled polygon for the region.
        assert "fill=blue!10" in latex

    def test_falls_back_to_fbox_when_empty(self):
        # x ≥ 5 AND x ≤ 1 → empty region.
        f = OptimizationRegionFigure(constraints=[
            (1, 0, "ge", 5),
            (1, 0, "le", 1),
            (0, 1, "ge", 0),
            (0, 1, "le", 10),
        ])
        latex = f.to_latex()
        assert r"\fbox{" in latex


class TestEqualityConstraint:
    def test_equality_yields_segment_region(self):
        # x + y = 5 inside the unit-square box → a line segment region.
        f = OptimizationRegionFigure(constraints=[
            (1, 1, "eq", 5),
            (1, 0, "ge", 0),
            (0, 1, "ge", 0),
            (1, 0, "le", 5),
            (0, 1, "le", 5),
        ])
        # 2 vertices = degenerate line segment, but still renders.
        assert len(f._vertices) == 2
        svg = f.to_svg()
        root = _parse(svg)
        ns = "{http://www.w3.org/2000/svg}"
        # Polygon element still present (degenerate-segment branch).
        assert root.findall(f".//{ns}polygon")


class TestEmptyRegion:
    def test_empty_region_does_not_crash(self):
        # Inconsistent constraints → no feasible region.
        f = OptimizationRegionFigure(constraints=[
            (1, 0, "ge", 5),
            (1, 0, "le", 1),
            (0, 1, "ge", 0),
            (0, 1, "le", 10),
        ])
        assert f._vertices == []
        svg = f.to_svg()
        # Polygon element still emitted (empty points attribute).
        root = _parse(svg)
        ns = "{http://www.w3.org/2000/svg}"
        polys = root.findall(f".//{ns}polygon")
        assert polys
        # to_text reports the empty case.
        assert "No feasible region" in f.to_text()


class TestObjectiveArrow:
    def test_arrow_drawn_when_objective_supplied(self):
        f = OptimizationRegionFigure(
            constraints=CANONICAL_CONSTRAINTS,
            objective_coeffs=(3, 2),
        )
        svg = f.to_svg()
        root = _parse(svg)
        ns = "{http://www.w3.org/2000/svg}"
        # Three line elements with the arrow stroke colour (shaft + 2 head segments).
        red_lines = [
            line for line in root.findall(f".//{ns}line")
            if line.get("stroke") == "#c33"
        ]
        assert len(red_lines) == 3

    def test_no_arrow_when_objective_omitted(self):
        f = OptimizationRegionFigure(constraints=CANONICAL_CONSTRAINTS)
        svg = f.to_svg()
        assert "#c33" not in svg


class TestValidation:
    def test_rejects_invalid_op(self):
        with pytest.raises(ValueError, match="op"):
            OptimizationRegionFigure(constraints=[(1, 1, "lt", 5)])

    def test_rejects_zero_coefficients(self):
        with pytest.raises(ValueError, match="cannot both be zero"):
            OptimizationRegionFigure(constraints=[(0, 0, "le", 5)])

    def test_rejects_empty_constraints(self):
        with pytest.raises(ValueError, match="at least one"):
            OptimizationRegionFigure(constraints=[])
