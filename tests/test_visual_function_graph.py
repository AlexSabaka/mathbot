"""Smoke tests for :class:`FunctionGraphFigure` (γ.3 A.2).

Covers the multi-format contract (SVG / text / TikZ), the new
annotation primitives (tangent, secant, area-shading, intercept,
critical-point, asymptote), the :class:`AxesAnnotation` companion,
and determinism. Every test parses the SVG output as XML so a
regression that breaks the SVG envelope fails loudly.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from src.visuals.figures.function_graph import (
    AxesAnnotation,
    FunctionGraphFigure,
)


SVG_NS = "{http://www.w3.org/2000/svg}"


def _parse(svg: str) -> ET.Element:
    """Parse an SVG string and return the root element."""
    try:
        return ET.fromstring(svg)
    except ET.ParseError as exc:  # pragma: no cover — diagnostic only
        pytest.fail(f"FunctionGraphFigure produced invalid XML: {exc}\n---\n{svg}")


# ---------------------------------------------------------------------------
# 1. Basic plot inheritance smoke test
# ---------------------------------------------------------------------------


class TestFunctionGraphInheritance:
    def test_basic_plot_renders(self):
        fig = FunctionGraphFigure(
            width=400, height=300,
            x_range=(-3, 3), y_range=(-2, 8),
            title="y = x squared",
        )
        fig.plot(lambda x: x ** 2)
        svg = fig.render()
        root = _parse(svg)
        assert root.tag == f"{SVG_NS}svg"
        # render() and to_svg() must agree.
        assert fig.render() == fig.to_svg()
        # Curve should produce at least one polyline.
        polylines = list(root.iter(f"{SVG_NS}polyline"))
        assert polylines, "expected at least one <polyline> for the curve"

    def test_no_annotations_means_no_extra_paths(self):
        # When no annotation is queued, the SVG should still be
        # well-formed and contain no shaded polygons / dashed asymptote
        # lines / red critical-point dots.
        fig = FunctionGraphFigure(x_range=(-3, 3))
        fig.plot(lambda x: x)
        root = _parse(fig.to_svg())
        assert not list(root.iter(f"{SVG_NS}polygon"))


# ---------------------------------------------------------------------------
# 2. tangent_at
# ---------------------------------------------------------------------------


class TestTangentAt:
    def test_tangent_renders_a_line(self):
        fig = FunctionGraphFigure(x_range=(-3, 3), y_range=(-2, 10))
        fig.plot(lambda x: x ** 2)
        fig.tangent_at(x=1, slope=2, length=2.0, label="y = 2x - 1")
        svg = fig.to_svg()
        # Tangent label and stroke colour should appear in the SVG.
        assert "y = 2x - 1" in svg
        assert "#16a34a" in svg  # tangent stroke
        root = _parse(svg)
        # At least one <line> with the tangent stroke colour.
        tangent_lines = [
            ln for ln in root.iter(f"{SVG_NS}line")
            if ln.get("stroke") == "#16a34a"
        ]
        assert len(tangent_lines) == 1

    def test_tangent_without_label_still_renders(self):
        fig = FunctionGraphFigure(x_range=(-3, 3), y_range=(-2, 10))
        fig.plot(lambda x: x ** 2)
        fig.tangent_at(x=1, slope=2)
        root = _parse(fig.to_svg())
        # No tangent text should be emitted, but the line stroke is.
        tangent_lines = [
            ln for ln in root.iter(f"{SVG_NS}line")
            if ln.get("stroke") == "#16a34a"
        ]
        assert tangent_lines


# ---------------------------------------------------------------------------
# 3. secant
# ---------------------------------------------------------------------------


class TestSecant:
    def test_secant_renders_a_dashed_line(self):
        fig = FunctionGraphFigure(x_range=(-3, 3), y_range=(-2, 10))
        fig.plot(lambda x: x ** 2)
        fig.secant(x1=0, x2=2, label="secant")
        svg = fig.to_svg()
        assert "secant" in svg
        assert "#7c3aed" in svg  # secant stroke colour
        root = _parse(svg)
        # Secant line must be dashed.
        secant_lines = [
            ln for ln in root.iter(f"{SVG_NS}line")
            if ln.get("stroke") == "#7c3aed"
        ]
        assert len(secant_lines) == 1
        assert secant_lines[0].get("stroke-dasharray") is not None


# ---------------------------------------------------------------------------
# 4. shade_area
# ---------------------------------------------------------------------------


class TestShadeArea:
    def test_shade_emits_polygon(self):
        fig = FunctionGraphFigure(x_range=(0, 3), y_range=(0, 10))
        fig.plot(lambda x: x ** 2)
        fig.shade_area(x1=0, x2=1, fill="#fbbf24")
        root = _parse(fig.to_svg())
        polygons = list(root.iter(f"{SVG_NS}polygon"))
        assert len(polygons) == 1
        assert polygons[0].get("fill") == "#fbbf24"
        # Polygon points must include at least three vertices.
        pts = polygons[0].get("points") or ""
        assert pts.count(",") >= 3

    def test_shade_without_curve_silently_skipped(self):
        # No curve queued → polygon falls back to nothing rather than
        # crashing. Lets partially authored templates still render.
        fig = FunctionGraphFigure(x_range=(0, 3))
        fig.shade_area(0, 1)
        root = _parse(fig.to_svg())
        assert not list(root.iter(f"{SVG_NS}polygon"))


# ---------------------------------------------------------------------------
# 5. mark_intercept
# ---------------------------------------------------------------------------


class TestMarkIntercept:
    def test_mark_intercept_x_axis(self):
        fig = FunctionGraphFigure(x_range=(-3, 3), y_range=(-2, 10))
        fig.plot(lambda x: x ** 2)
        fig.mark_intercept("x", 0, label="(0, 0)")
        svg = fig.to_svg()
        assert "(0, 0)" in svg
        assert "#1d4ed8" in svg
        root = _parse(svg)
        intercept_circles = [
            c for c in root.iter(f"{SVG_NS}circle")
            if c.get("fill") == "#1d4ed8"
        ]
        assert len(intercept_circles) == 1

    def test_mark_intercept_y_axis(self):
        fig = FunctionGraphFigure(x_range=(-3, 3), y_range=(-2, 10))
        fig.plot(lambda x: x ** 2)
        fig.mark_intercept("y", 4)
        root = _parse(fig.to_svg())
        intercept_circles = [
            c for c in root.iter(f"{SVG_NS}circle")
            if c.get("fill") == "#1d4ed8"
        ]
        assert len(intercept_circles) == 1

    def test_mark_intercept_invalid_axis(self):
        fig = FunctionGraphFigure()
        with pytest.raises(ValueError):
            fig.mark_intercept("z", 0)


# ---------------------------------------------------------------------------
# 6. mark_critical
# ---------------------------------------------------------------------------


class TestMarkCritical:
    def test_critical_emits_marker_and_dashed_guide(self):
        fig = FunctionGraphFigure(x_range=(-3, 3), y_range=(-2, 10))
        fig.plot(lambda x: x ** 2)
        fig.mark_critical(x=1.5, label="max")
        svg = fig.to_svg()
        assert "max" in svg
        assert "#dc2626" in svg
        root = _parse(svg)
        # Red dot.
        critical_dots = [
            c for c in root.iter(f"{SVG_NS}circle")
            if c.get("fill") == "#dc2626"
        ]
        assert len(critical_dots) == 1
        # Red dashed guide.
        critical_guides = [
            ln for ln in root.iter(f"{SVG_NS}line")
            if ln.get("stroke") == "#dc2626"
            and ln.get("stroke-dasharray") is not None
        ]
        assert len(critical_guides) == 1


# ---------------------------------------------------------------------------
# 7. mark_asymptote
# ---------------------------------------------------------------------------


class TestMarkAsymptote:
    def test_horizontal_asymptote_is_dashed(self):
        fig = FunctionGraphFigure(x_range=(-3, 3), y_range=(-2, 10))
        fig.plot(lambda x: x ** 2)
        fig.mark_asymptote(value=4, kind="horizontal", label="y = 4")
        svg = fig.to_svg()
        assert "y = 4" in svg
        root = _parse(svg)
        asy_lines = [
            ln for ln in root.iter(f"{SVG_NS}line")
            if ln.get("stroke") == "#9333ea"
            and ln.get("stroke-dasharray") is not None
        ]
        assert len(asy_lines) == 1

    def test_vertical_asymptote_renders(self):
        fig = FunctionGraphFigure(x_range=(-3, 3), y_range=(-10, 10))
        fig.plot(lambda x: x)
        fig.mark_asymptote(value=2, kind="vertical", label="x = 2")
        svg = fig.to_svg()
        assert "x = 2" in svg
        root = _parse(svg)
        asy_lines = [
            ln for ln in root.iter(f"{SVG_NS}line")
            if ln.get("stroke") == "#9333ea"
        ]
        assert len(asy_lines) == 1

    def test_invalid_kind(self):
        fig = FunctionGraphFigure()
        with pytest.raises(ValueError):
            fig.mark_asymptote(0, kind="diagonal")


# ---------------------------------------------------------------------------
# 8. AxesAnnotation.apply
# ---------------------------------------------------------------------------


class TestAxesAnnotation:
    def test_apply_delegates_to_fig_methods(self):
        fig = FunctionGraphFigure(x_range=(-3, 3), y_range=(-2, 10))
        fig.plot(lambda x: x ** 2)
        ann = AxesAnnotation(
            intercepts=[("x", 0.0), ("y", 0.0)],
            asymptotes=[("horizontal", 4.0)],
            critical_points=[(1.5, "max")],
        )
        ann.apply(fig)
        # Each list should populate the corresponding queue.
        assert len(fig._intercepts) == 2
        assert len(fig._asymptotes) == 1
        assert len(fig._criticals) == 1


# ---------------------------------------------------------------------------
# 9. add_axes_annotation
# ---------------------------------------------------------------------------


class TestAddAxesAnnotation:
    def test_bundle_applied_in_one_call(self):
        fig = FunctionGraphFigure(x_range=(-3, 3), y_range=(-2, 10))
        fig.plot(lambda x: x ** 2)
        ann = AxesAnnotation(
            intercepts=[("x", 0.0)],
            asymptotes=[("horizontal", 4.0)],
            critical_points=[(1.5, "max")],
        )
        result = fig.add_axes_annotation(ann)
        # Fluent API — returns self.
        assert result is fig
        svg = fig.to_svg()
        # All three annotation types should land in the SVG.
        assert "max" in svg
        # Intercept marker (blue) and asymptote (purple) colours.
        assert "#1d4ed8" in svg
        assert "#9333ea" in svg


# ---------------------------------------------------------------------------
# 10. Determinism
# ---------------------------------------------------------------------------


class TestDeterminism:
    def test_same_inputs_same_bytes(self):
        def build():
            fig = FunctionGraphFigure(
                width=400, height=300,
                x_range=(-3, 3), y_range=(-2, 10),
                title="y = x²",
            )
            fig.plot(lambda x: x ** 2)
            fig.tangent_at(x=1, slope=2, label="y = 2x - 1")
            fig.secant(x1=0, x2=2, label="secant")
            fig.shade_area(x1=0, x2=1, fill="#fbbf24")
            fig.mark_intercept("x", 0, label="(0, 0)")
            fig.mark_critical(x=1.5, label="max")
            fig.mark_asymptote(value=4, kind="horizontal", label="y = 4")
            return fig.to_svg()

        a = build()
        b = build()
        assert a == b


# ---------------------------------------------------------------------------
# 11. to_text — mentions all annotations in canonical order
# ---------------------------------------------------------------------------


class TestToText:
    def test_to_text_lists_every_annotation(self):
        fig = FunctionGraphFigure(
            x_range=(-3, 3), y_range=(-2, 10), title="y = x²",
        )
        fig.plot(lambda x: x ** 2)
        fig.tangent_at(x=1, slope=2, label="y = 2x - 1")
        fig.secant(x1=0, x2=2, label="secant")
        fig.shade_area(x1=0, x2=1)
        fig.mark_intercept("x", 0, label="(0, 0)")
        fig.mark_critical(x=1.5, label="max")
        fig.mark_asymptote(value=4, kind="horizontal", label="y = 4")
        text = fig.to_text()
        # Plot mentioned.
        assert "Plot of" in text
        # Each annotation type referenced.
        assert "Tangent line" in text
        assert "Secant line" in text
        assert "Shaded area" in text
        assert "Intercept" in text
        assert "critical point" in text.lower()
        assert "asymptote" in text.lower()
        # Canonical ordering: tangent → secant → shaded → intercept →
        # critical → asymptote.
        order_indexes = [
            text.index("Tangent line"),
            text.index("Secant line"),
            text.index("Shaded area"),
            text.index("Intercept"),
            text.lower().index("critical point"),
            text.lower().index("asymptote"),
        ]
        assert order_indexes == sorted(order_indexes)

    def test_to_text_without_curve(self):
        fig = FunctionGraphFigure(x_range=(-3, 3))
        text = fig.to_text()
        assert "no curve" in text.lower()


# ---------------------------------------------------------------------------
# 12. to_latex
# ---------------------------------------------------------------------------


class TestToLatex:
    def test_to_latex_returns_non_empty(self):
        fig = FunctionGraphFigure(x_range=(-3, 3), y_range=(-2, 10))
        fig.plot(lambda x: x ** 2)
        fig.tangent_at(x=1, slope=2, label="y = 2x - 1")
        latex = fig.to_latex()
        assert latex
        assert r"\begin{tikzpicture}" in latex
        assert r"\end{tikzpicture}" in latex
        # Tangent line drawn in green.
        assert "green" in latex

    def test_to_latex_falls_back_when_no_curve(self):
        # Empty figure → \fbox fallback (still compiles in LaTeX).
        fig = FunctionGraphFigure()
        latex = fig.to_latex()
        assert latex.startswith(r"\fbox")
