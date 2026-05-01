"""Tests for the Phase γ.3 (A.2) ``RiverbankFigure`` builder.

Stewart's parallel-banks optimization figure. The builder ships SVG,
plain-text, and TikZ outputs; tests cover the structural invariants
(banks rendered, P/Q markers present, brace labels appear) plus
determinism and a couple of edge cases for the ``swim_x`` parameter.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from src.visuals.figures.riverbank import RiverbankFigure


SVG_NS = "http://www.w3.org/2000/svg"


def _parse(svg: str) -> ET.Element:
    """Parse an SVG string and return its root element."""
    return ET.fromstring(svg)


def _findall(root: ET.Element, tag: str):
    return root.findall(f"{{{SVG_NS}}}{tag}")


class TestRiverbankFigureSVG:
    def test_default_renders_valid_svg(self):
        svg = RiverbankFigure().to_svg()
        root = _parse(svg)
        assert root.tag == f"{{{SVG_NS}}}svg"

    def test_both_banks_and_endpoint_markers_rendered(self):
        svg = RiverbankFigure().to_svg()
        root = _parse(svg)
        # The two horizontal bank lines are at y=80 and y=200 by
        # construction; assert at least two horizontal lines with
        # those y values.
        lines = _findall(root, "line")
        bank_ys = sorted({
            line.get("y1")
            for line in lines
            if line.get("y1") == line.get("y2")
            and line.get("y1") in {"80", "200"}
        })
        assert bank_ys == ["200", "80"]

        # P and Q endpoint markers — radius 5 circles by construction.
        circles = _findall(root, "circle")
        endpoint_circles = [c for c in circles if c.get("r") == "5"]
        assert len(endpoint_circles) == 2

    def test_no_swim_path_when_swim_x_unset(self):
        svg = RiverbankFigure().to_svg()
        root = _parse(svg)
        # Path legs are dashed lines with stroke-dasharray="6 4".
        dashed = [
            line
            for line in _findall(root, "line")
            if line.get("stroke-dasharray") == "6 4"
        ]
        assert dashed == []
        # No swim-point marker either.
        circles = _findall(root, "circle")
        assert all(c.get("r") != "4" for c in circles)

    def test_swim_path_renders_two_dashed_segments_and_marker(self):
        svg = RiverbankFigure(swim_x=2).to_svg()
        root = _parse(svg)
        dashed = [
            line
            for line in _findall(root, "line")
            if line.get("stroke-dasharray") == "6 4"
        ]
        assert len(dashed) == 2
        # Swim-point marker is a radius-4 circle.
        swim_markers = [
            c for c in _findall(root, "circle") if c.get("r") == "4"
        ]
        assert len(swim_markers) == 1

    def test_distance_and_downstream_labels_appear(self):
        fig = RiverbankFigure(label_distance="d", label_downstream="8 km")
        svg = fig.to_svg()
        assert ">d</text>" in svg
        assert ">8 km</text>" in svg

    def test_swim_label_appears_only_when_swim_x_set(self):
        # No swim_x → no swim-x label.
        no_swim = RiverbankFigure(label_swim="x").to_svg()
        # We can't simply test "x" presence (the substring may appear
        # elsewhere), but the swim brace introduces the standalone
        # text element ">x</text>".
        assert ">x</text>" not in no_swim
        # With swim_x → swim label is present.
        with_swim = RiverbankFigure(swim_x=2, label_swim="x").to_svg()
        assert ">x</text>" in with_swim

    def test_render_is_deterministic(self):
        a = RiverbankFigure(bank_distance=3, downstream=8, swim_x=2).render()
        b = RiverbankFigure(bank_distance=3, downstream=8, swim_x=2).render()
        assert a == b
        # And the same as to_svg().
        assert a == RiverbankFigure(
            bank_distance=3, downstream=8, swim_x=2
        ).to_svg()


class TestRiverbankFigureText:
    def test_text_mentions_all_parameters(self):
        text = RiverbankFigure(
            bank_distance=3, downstream=8, swim_x=2
        ).to_text()
        assert "3 units" in text
        assert "8 units" in text
        assert "P" in text and "Q" in text
        assert "x=2" in text

    def test_text_omits_swim_when_not_provided(self):
        text = RiverbankFigure().to_text()
        assert "candidate path" not in text


class TestRiverbankFigureLatex:
    def test_latex_emits_tikzpicture(self):
        latex = RiverbankFigure().to_latex()
        assert r"\begin{tikzpicture}" in latex
        assert r"\end{tikzpicture}" in latex

    def test_latex_includes_swim_path_when_set(self):
        latex = RiverbankFigure(swim_x=2).to_latex()
        assert r"\filldraw (2," in latex
        assert "dashed" in latex

    def test_latex_fbox_fallback_for_zero_downstream(self):
        latex = RiverbankFigure(downstream=0).to_latex()
        assert r"\fbox" in latex


class TestRiverbankFigureEdgeCases:
    def test_swim_x_zero_renders_two_segments(self):
        # P → S(at x=0, bottom) is a vertical drop; S → Q runs along
        # the bottom bank. Both legs are still rendered as dashed
        # lines.
        svg = RiverbankFigure(swim_x=0, downstream=8).to_svg()
        root = _parse(svg)
        dashed = [
            line
            for line in _findall(root, "line")
            if line.get("stroke-dasharray") == "6 4"
        ]
        assert len(dashed) == 2

    def test_swim_x_equals_downstream_renders_two_segments(self):
        # P → S coincides with P → Q (a single diagonal); the second
        # leg S → Q has zero length but the builder still emits a
        # line element for it (so the schema is invariant).
        svg = RiverbankFigure(swim_x=8, downstream=8).to_svg()
        root = _parse(svg)
        dashed = [
            line
            for line in _findall(root, "line")
            if line.get("stroke-dasharray") == "6 4"
        ]
        assert len(dashed) == 2
