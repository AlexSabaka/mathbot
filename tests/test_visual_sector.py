"""Smoke tests for :class:`SectorFigure` (γ.3 A.2).

Covers the multi-format contract (SVG / text / TikZ), determinism,
and the two interesting edge cases (``angle_deg == 360`` collapses
to a full disc; ``cutout_deg == angle_deg`` degenerates to a sector
fully overdrawn by its own cutout). The shared visual fixture
suite (`tests/test_visual.py`) stays untouched — these focus on
the new builder.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from src.visuals.figures.sector import SectorFigure


SVG_NS = "{http://www.w3.org/2000/svg}"


def _parse(svg: str) -> ET.Element:
    """Parse an SVG string and return the root element.

    Raises a clearly-flagged failure if the SVG is malformed — XML
    parse errors here mean we've broken the SVG envelope.
    """
    try:
        return ET.fromstring(svg)
    except ET.ParseError as exc:  # pragma: no cover — diagnostic only
        pytest.fail(f"SectorFigure produced invalid XML: {exc}\n---\n{svg}")


class TestSectorFigureSVG:
    def test_basic_render_is_well_formed(self):
        fig = SectorFigure(radius=100, angle_deg=120)
        svg = fig.to_svg()
        root = _parse(svg)
        # Root element must be the SVG element with our namespace.
        assert root.tag == f"{SVG_NS}svg"
        # And `render()` must return the same thing as `to_svg()`.
        assert fig.render() == svg

    def test_labels_appear_in_svg(self):
        fig = SectorFigure(
            radius=100,
            angle_deg=120,
            label_radius="r = 10 cm",
            label_angle="θ = 120°",
        )
        svg = fig.to_svg()
        # _esc lets non-ASCII through untouched, so the labels survive
        # round-trip into the SVG body verbatim.
        assert "r = 10 cm" in svg
        assert "θ = 120°" in svg
        # Both labels render as <text> elements.
        root = _parse(svg)
        texts = [t.text for t in root.iter(f"{SVG_NS}text")]
        assert "r = 10 cm" in texts
        assert "θ = 120°" in texts

    def test_no_cutout_renders_one_path(self):
        fig = SectorFigure(radius=100, angle_deg=120, cutout_deg=0)
        root = _parse(fig.to_svg())
        paths = list(root.iter(f"{SVG_NS}path"))
        assert len(paths) == 1, "cutout_deg=0 should emit exactly one sector path"

    def test_with_cutout_renders_two_paths(self):
        fig = SectorFigure(radius=100, angle_deg=120, cutout_deg=30)
        root = _parse(fig.to_svg())
        paths = list(root.iter(f"{SVG_NS}path"))
        assert len(paths) == 2, "cutout_deg>0 should emit outer sector + cutout"
        # Cutout fill must be white so it visually erases the sector.
        fills = {p.get("fill") for p in paths}
        assert "#ffffff" in fills

    def test_determinism(self):
        # Same inputs → identical bytes. The fixture-drift lint relies
        # on this property project-wide; covering it explicitly here
        # catches regressions before they reach the corpus.
        a = SectorFigure(
            radius=100, angle_deg=120, cutout_deg=30,
            label_radius="r = 10", label_angle="θ = 120°",
        ).to_svg()
        b = SectorFigure(
            radius=100, angle_deg=120, cutout_deg=30,
            label_radius="r = 10", label_angle="θ = 120°",
        ).to_svg()
        assert a == b


class TestSectorFigureText:
    def test_to_text_mentions_parameters(self):
        text = SectorFigure(radius=10, angle_deg=120).to_text()
        assert "10" in text
        assert "120" in text
        # No cutout → cutout phrase should not appear.
        assert "cut out" not in text

    def test_to_text_mentions_cutout(self):
        text = SectorFigure(radius=10, angle_deg=120, cutout_deg=30).to_text()
        assert "30" in text
        assert "cut out" in text

    def test_to_text_includes_labels_when_present(self):
        text = SectorFigure(
            radius=10, angle_deg=120,
            label_radius="r = 10 cm", label_angle="θ = 120°",
        ).to_text()
        assert "r = 10 cm" in text
        assert "θ = 120°" in text


class TestSectorFigureLatex:
    def test_to_latex_uses_tikz(self):
        latex = SectorFigure(radius=100, angle_deg=120).to_latex()
        assert r"\begin{tikzpicture}" in latex
        assert r"\end{tikzpicture}" in latex
        # Real TikZ arc syntax — the ``arc[`` token guards against a
        # silent regression to the ``\fbox{[Figure: ...]}`` fallback.
        assert "arc[" in latex

    def test_to_latex_emits_cutout_when_requested(self):
        latex = SectorFigure(radius=100, angle_deg=120, cutout_deg=30).to_latex()
        # Two ``\draw`` commands: one for the sector, one for the cutout.
        assert latex.count(r"\draw") >= 2


class TestSectorFigureEdgeCases:
    def test_full_circle_renders(self):
        # angle_deg = 360 → full disc. The sector_path special-cases
        # this (start == end would otherwise render an empty arc) by
        # splitting into two semi-arcs.
        fig = SectorFigure(radius=80, angle_deg=360)
        svg = fig.to_svg()
        _parse(svg)  # well-formed
        # Should still emit exactly one outer-sector path.
        root = _parse(svg)
        paths = list(root.iter(f"{SVG_NS}path"))
        assert len(paths) == 1

    def test_cutout_equal_to_sector_does_not_crash(self):
        # Degenerate but valid: the cutout swallows the sector. Should
        # render two paths (no NaN coordinates, no exceptions).
        fig = SectorFigure(radius=100, angle_deg=120, cutout_deg=120)
        svg = fig.to_svg()
        root = _parse(svg)
        paths = list(root.iter(f"{SVG_NS}path"))
        assert len(paths) == 2

    def test_invalid_radius_rejected(self):
        with pytest.raises(ValueError):
            SectorFigure(radius=0, angle_deg=120)

    def test_invalid_angle_rejected(self):
        with pytest.raises(ValueError):
            SectorFigure(radius=100, angle_deg=0)
