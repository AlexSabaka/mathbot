"""γ.3 (A.2) — tests for ConeNetFigure.

The cone-net figure ships the multi-format trio (`to_svg`, `to_text`,
`to_latex`) plus a determinism check. Coverage targets the geometry
labels (slant + base radius must both appear), the structural
existence of the two side-by-side regions (≥2 path/polygon nodes),
and two edge-case regimes (sector_angle_deg=360 and very small base
radius) that pedagogical templates may legitimately request.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from src.visuals.figures.cone_net import ConeNetFigure


SVG_NS = "{http://www.w3.org/2000/svg}"


def _count(root: ET.Element, tag: str) -> int:
    return len(root.findall(f".//{SVG_NS}{tag}"))


class TestConeNetFigure:
    def test_to_svg_parses_as_xml(self):
        svg = ConeNetFigure().to_svg()
        root = ET.fromstring(svg)
        assert root.tag.endswith("svg")
        # Default canvas dims propagate through.
        assert root.attrib["width"] == "600"
        assert root.attrib["height"] == "320"

    def test_labels_appear(self):
        svg = ConeNetFigure(slant=10, base_radius=6, height=8).to_svg()
        # Slant label shows on both halves; base radius `r = ...`
        # shows on the cone half. Both must be in the source.
        assert "slant" in svg
        assert "10" in svg
        assert "r = 6" in svg
        assert "h = 8" in svg

    def test_structural_paths_present(self):
        """At least one path/polygon per region (sector + cone)."""
        svg = ConeNetFigure().to_svg()
        root = ET.fromstring(svg)
        path_like = _count(root, "path") + _count(root, "polygon")
        # Sector path + cone polygon + visible/back base arcs ≥ 4,
        # but the contract only requires ≥ 2.
        assert path_like >= 2

    def test_determinism(self):
        a = ConeNetFigure(slant=12, sector_angle_deg=180,
                          base_radius=4, height=6).to_svg()
        b = ConeNetFigure(slant=12, sector_angle_deg=180,
                          base_radius=4, height=6).to_svg()
        assert a == b

    def test_to_text_mentions_all_inputs(self):
        text = ConeNetFigure(
            slant=10, sector_angle_deg=216,
            base_radius=6, height=8,
        ).to_text()
        assert "slant" in text.lower()
        assert "10" in text
        assert "216" in text
        assert "6" in text
        assert "8" in text

    def test_to_latex_has_tikz_or_fbox(self):
        latex = ConeNetFigure().to_latex()
        assert ("tikzpicture" in latex) or ("fbox" in latex)

    def test_full_disk_sector_renders(self):
        """sector_angle_deg=360 → flat-disk lateral surface.

        Geometrically degenerate (the cone height collapses) but the
        figure must still render without raising and produce parseable
        SVG. LaTeX falls back to fbox in this regime.
        """
        fig = ConeNetFigure(sector_angle_deg=360,
                            base_radius=10, height=0.01)
        svg = fig.to_svg()
        ET.fromstring(svg)  # raises if malformed
        assert "fbox" in fig.to_latex()

    def test_tiny_base_radius(self):
        """Very small base radius — should not divide-by-zero or clip."""
        fig = ConeNetFigure(slant=5, sector_angle_deg=10,
                            base_radius=0.05, height=5)
        svg = fig.to_svg()
        ET.fromstring(svg)
        # Slant label should still be present at this scale.
        assert "slant" in svg
