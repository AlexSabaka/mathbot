"""Smoke tests for :class:`TriangleFigure` (γ.3 A.2).

Covers the multi-format contract (SVG / text / TikZ), determinism,
and the geometry overlays (altitude / median / angle bisector) plus
the degenerate-vertices edge case.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from src.visuals.figures.triangle import TriangleFigure


SVG_NS = "{http://www.w3.org/2000/svg}"


def _parse(svg: str) -> ET.Element:
    """Parse an SVG string and return the root element.

    Raises a clearly-flagged failure if the SVG is malformed — XML
    parse errors here mean we've broken the SVG envelope.
    """
    try:
        return ET.fromstring(svg)
    except ET.ParseError as exc:  # pragma: no cover — diagnostic only
        pytest.fail(f"TriangleFigure produced invalid XML: {exc}\n---\n{svg}")


class TestTriangleFigureSVG:
    def test_default_render_is_well_formed(self):
        fig = TriangleFigure()
        svg = fig.to_svg()
        root = _parse(svg)
        assert root.tag == f"{SVG_NS}svg"
        # render() must agree with to_svg().
        assert fig.render() == svg
        # Default render emits exactly one <polygon> for the outline.
        polys = list(root.iter(f"{SVG_NS}polygon"))
        assert len(polys) == 1

    def test_vertex_and_side_labels_appear(self):
        fig = TriangleFigure(
            side_labels={"AB": "5 cm", "BC": "4 cm", "CA": "3 cm"},
            vertex_labels={"A": "Apex", "B": "Base-L", "C": "Base-R"},
        )
        svg = fig.to_svg()
        # All custom labels survive into the SVG body.
        for tok in ("Apex", "Base-L", "Base-R", "5 cm", "4 cm", "3 cm"):
            assert tok in svg
        # Each appears as the text of a <text> element.
        root = _parse(svg)
        texts = [t.text for t in root.iter(f"{SVG_NS}text")]
        for tok in ("Apex", "Base-L", "Base-R", "5 cm", "4 cm", "3 cm"):
            assert tok in texts

    def test_angle_labels_appear(self):
        fig = TriangleFigure(
            angle_labels={"A": "30°", "B": "60°", "C": "90°"},
        )
        svg = fig.to_svg()
        root = _parse(svg)
        texts = [t.text for t in root.iter(f"{SVG_NS}text")]
        assert "30°" in texts
        assert "60°" in texts
        assert "90°" in texts

    def test_add_altitude_emits_dashed_line(self):
        fig = TriangleFigure()
        fig.add_altitude("C")
        root = _parse(fig.to_svg())
        # <line> elements with stroke-dasharray are our overlay markers.
        dashed = [
            line for line in root.iter(f"{SVG_NS}line")
            if line.get("stroke-dasharray")
        ]
        assert len(dashed) == 1
        # Altitude pattern is the 6,4 dash.
        assert dashed[0].get("stroke-dasharray") == "6,4"

    def test_add_median_emits_dashdot_line(self):
        fig = TriangleFigure()
        fig.add_median("A")
        root = _parse(fig.to_svg())
        # The median uses a dash-dot stroke pattern (4 numbers).
        dashed = [
            line for line in root.iter(f"{SVG_NS}line")
            if line.get("stroke-dasharray")
        ]
        assert len(dashed) == 1
        # Dash-dot pattern has 4 segments.
        assert dashed[0].get("stroke-dasharray") == "6,3,2,3"

    def test_add_angle_bisector_emits_dashed_line(self):
        fig = TriangleFigure()
        fig.add_angle_bisector("B")
        root = _parse(fig.to_svg())
        dashed = [
            line for line in root.iter(f"{SVG_NS}line")
            if line.get("stroke-dasharray")
        ]
        assert len(dashed) == 1
        assert dashed[0].get("stroke-dasharray") == "4,3"

    def test_multiple_overlays(self):
        # A triangle with all three overlays should render three dashed
        # lines, one per overlay.
        fig = TriangleFigure()
        fig.add_altitude("C")
        fig.add_median("A")
        fig.add_angle_bisector("B")
        root = _parse(fig.to_svg())
        dashed = [
            line for line in root.iter(f"{SVG_NS}line")
            if line.get("stroke-dasharray")
        ]
        assert len(dashed) == 3

    def test_idempotent_overlay_adds(self):
        # Calling add_altitude("C") twice should still render only one
        # altitude. The fixture-drift lint depends on this.
        fig = TriangleFigure()
        fig.add_altitude("C")
        fig.add_altitude("C")
        root = _parse(fig.to_svg())
        dashed = [
            line for line in root.iter(f"{SVG_NS}line")
            if line.get("stroke-dasharray")
        ]
        assert len(dashed) == 1

    def test_invalid_vertex_name_rejected(self):
        with pytest.raises(ValueError):
            TriangleFigure().add_altitude("Z")

    def test_invalid_vertex_count_rejected(self):
        with pytest.raises(ValueError):
            TriangleFigure(vertices=[(0, 0), (1, 0)])

    def test_determinism(self):
        # Same inputs + same overlay sequence → identical bytes.
        a = TriangleFigure(
            side_labels={"AB": "5"}, angle_labels={"A": "30°"},
        )
        a.add_altitude("C")
        a.add_median("A")
        b = TriangleFigure(
            side_labels={"AB": "5"}, angle_labels={"A": "30°"},
        )
        b.add_altitude("C")
        b.add_median("A")
        assert a.to_svg() == b.to_svg()


class TestTriangleFigureText:
    def test_to_text_mentions_all_vertices(self):
        text = TriangleFigure().to_text()
        # Default vertices are (0, 0), (4, 0), (1, 3).
        assert "(0, 0)" in text
        assert "(4, 0)" in text
        assert "(1, 3)" in text

    def test_to_text_mentions_side_labels(self):
        text = TriangleFigure(
            side_labels={"AB": "5 cm", "BC": "4 cm"},
        ).to_text()
        assert "AB = 5 cm" in text
        assert "BC = 4 cm" in text
        # Unlabelled side renders as ``CA = ?`` so the reader sees the
        # gap rather than missing the side entirely.
        assert "CA = ?" in text

    def test_to_text_mentions_overlays(self):
        fig = TriangleFigure()
        fig.add_altitude("C")
        fig.add_median("A")
        fig.add_angle_bisector("B")
        text = fig.to_text().lower()
        assert "altitude from c" in text
        assert "median from a" in text
        assert "angle bisector from b" in text


class TestTriangleFigureLatex:
    def test_to_latex_uses_tikz(self):
        latex = TriangleFigure().to_latex()
        assert r"\begin{tikzpicture}" in latex
        assert r"\end{tikzpicture}" in latex
        # Canonical "(A) -- (B) -- (C) -- cycle" idiom.
        assert "(A) -- (B) -- (C) -- cycle" in latex

    def test_to_latex_includes_overlays(self):
        fig = TriangleFigure()
        fig.add_altitude("C")
        fig.add_median("A")
        latex = fig.to_latex()
        assert "dashed" in latex
        assert "dash dot" in latex


class TestTriangleFigureEdgeCases:
    def test_collinear_vertices_render_without_crashing(self):
        # Degenerate but valid: all three vertices on a horizontal line.
        # The auto-fit math has to fall back gracefully (zero y-extent
        # would otherwise produce a divide-by-zero).
        fig = TriangleFigure(vertices=[(0, 0), (1, 0), (2, 0)])
        svg = fig.to_svg()
        # XML parse must succeed.
        _parse(svg)
        # And to_text shouldn't crash either.
        assert "Triangle" in fig.to_text()

    def test_collinear_vertices_skip_degenerate_bisector(self):
        # When all three vertices coincide, bisector geometry returns
        # ``None`` and the overlay should silently skip rather than
        # crash. (The SVG still renders the empty triangle.)
        fig = TriangleFigure(vertices=[(0, 0), (0, 0), (0, 0)])
        fig.add_angle_bisector("A")
        svg = fig.to_svg()
        root = _parse(svg)
        # No dashed line should be emitted because the bisector
        # endpoint is undefined for a fully-degenerate triangle.
        dashed = [
            line for line in root.iter(f"{SVG_NS}line")
            if line.get("stroke-dasharray")
        ]
        assert dashed == []
