"""Smoke tests for :class:`RelatedRatesGeometry` (γ.3 A.2).

Covers the 5-way setup dispatcher's per-sub-case SVG/text/LaTeX output,
the ValueError on invalid setup strings, and determinism.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from src.visuals.figures.related_rates import RelatedRatesGeometry


SVG_NS = "{http://www.w3.org/2000/svg}"


def _parse(svg: str) -> ET.Element:
    """Parse SVG text → root element. Fail clearly on malformed XML."""
    try:
        return ET.fromstring(svg)
    except ET.ParseError as exc:  # pragma: no cover — diagnostic only
        pytest.fail(f"RelatedRatesGeometry produced invalid XML: {exc}\n---\n{svg}")


# ---------------------------------------------------------------------------
# Per-setup SVG round-trip — instantiate w/ defaults, parse, assert key
# author-supplied labels survive through to <text> bodies.
# ---------------------------------------------------------------------------


class TestLadderSliding:
    def test_svg_round_trip(self):
        fig = RelatedRatesGeometry(
            setup="ladder_sliding",
            ladder_length=10,
            base_distance=6,
            label_ladder="ℓ = 10",
            label_base="x = 6",
            label_height="y",
        )
        svg = fig.to_svg()
        root = _parse(svg)
        assert root.tag == f"{SVG_NS}svg"
        texts = [t.text for t in root.iter(f"{SVG_NS}text")]
        assert "ℓ = 10" in texts
        assert "x = 6" in texts
        assert "y" in texts
        # Geometry: ladder, wall, ground = at least 3 line elements.
        lines = list(root.iter(f"{SVG_NS}line"))
        assert len(lines) >= 3

    def test_to_text_mentions_params(self):
        text = RelatedRatesGeometry(setup="ladder_sliding").to_text()
        assert "ladder" in text.lower()
        assert "10" in text  # default ladder_length
        assert "6" in text   # default base_distance


class TestConeDraining:
    def test_svg_round_trip(self):
        fig = RelatedRatesGeometry(
            setup="cone_draining",
            radius_top=4, height=10, water_height=6,
            label_radius="r_top = 4",
            label_height="h = 10",
            label_water="water = 6",
        )
        svg = fig.to_svg()
        root = _parse(svg)
        assert root.tag == f"{SVG_NS}svg"
        texts = [t.text for t in root.iter(f"{SVG_NS}text")]
        assert "r_top = 4" in texts
        assert "h = 10" in texts
        assert "water = 6" in texts
        # Cone has rim ellipse + (water surface) ellipse → at least 1 ellipse.
        ellipses = list(root.iter(f"{SVG_NS}ellipse"))
        assert len(ellipses) >= 1

    def test_to_text_mentions_params(self):
        text = RelatedRatesGeometry(setup="cone_draining").to_text()
        assert "conical" in text.lower() or "cone" in text.lower()
        assert "4" in text
        assert "10" in text
        assert "6" in text


class TestBalloonInflating:
    def test_svg_round_trip(self):
        fig = RelatedRatesGeometry(
            setup="balloon_inflating", radius=5, label_radius="r = 5",
        )
        svg = fig.to_svg()
        root = _parse(svg)
        assert root.tag == f"{SVG_NS}svg"
        texts = [t.text for t in root.iter(f"{SVG_NS}text")]
        assert "r = 5" in texts
        # Balloon has solid + dashed circles + center dot → ≥ 3 circles.
        circles = list(root.iter(f"{SVG_NS}circle"))
        assert len(circles) >= 3

    def test_to_text_mentions_params(self):
        text = RelatedRatesGeometry(setup="balloon_inflating").to_text()
        assert "balloon" in text.lower()
        assert "5" in text


class TestShadowLengthening:
    def test_svg_round_trip(self):
        fig = RelatedRatesGeometry(
            setup="shadow_lengthening",
            pole_height=15, person_height=6,
            person_distance=10, shadow_length=4,
            label_pole="L = 15",
            label_person="h = 6",
            label_distance="d = 10",
            label_shadow="s = 4",
        )
        svg = fig.to_svg()
        root = _parse(svg)
        assert root.tag == f"{SVG_NS}svg"
        texts = [t.text for t in root.iter(f"{SVG_NS}text")]
        assert "L = 15" in texts
        assert "h = 6" in texts
        assert "d = 10" in texts
        assert "s = 4" in texts

    def test_to_text_mentions_params(self):
        text = RelatedRatesGeometry(setup="shadow_lengthening").to_text()
        assert "shadow" in text.lower()
        assert "15" in text
        assert "6" in text


class TestBoatPulledToDock:
    def test_svg_round_trip(self):
        fig = RelatedRatesGeometry(
            setup="boat_pulled_to_dock",
            dock_height=4, rope_length=10, boat_distance=8,
            label_dock="dock", label_rope="ℓ = 10", label_distance="x = 8",
        )
        svg = fig.to_svg()
        root = _parse(svg)
        assert root.tag == f"{SVG_NS}svg"
        texts = [t.text for t in root.iter(f"{SVG_NS}text")]
        assert "dock" in texts
        assert "ℓ = 10" in texts
        assert "x = 8" in texts

    def test_to_text_mentions_params(self):
        text = RelatedRatesGeometry(setup="boat_pulled_to_dock").to_text()
        assert "boat" in text.lower()
        assert "dock" in text.lower()
        assert "8" in text
        assert "10" in text


# ---------------------------------------------------------------------------
# Cross-cutting tests — invalid input, determinism, render() contract,
# multi-format coverage.
# ---------------------------------------------------------------------------


class TestDispatcher:
    def test_invalid_setup_raises_value_error(self):
        with pytest.raises(ValueError):
            RelatedRatesGeometry(setup="not_a_real_setup")

    def test_render_matches_to_svg(self):
        # `Visual = builder.render()` is the visual-sandbox contract;
        # render() should be a thin alias for to_svg().
        fig = RelatedRatesGeometry(setup="cone_draining")
        assert fig.render() == fig.to_svg()

    def test_determinism(self):
        # Same inputs → byte-identical SVG. The fixture-drift lint
        # relies on this property project-wide.
        for setup in [
            "ladder_sliding", "cone_draining", "balloon_inflating",
            "shadow_lengthening", "boat_pulled_to_dock",
        ]:
            a = RelatedRatesGeometry(setup=setup).to_svg()
            b = RelatedRatesGeometry(setup=setup).to_svg()
            assert a == b, f"{setup} not deterministic"

    def test_to_latex_non_empty_for_all_setups(self):
        for setup in [
            "ladder_sliding", "cone_draining", "balloon_inflating",
            "shadow_lengthening", "boat_pulled_to_dock",
        ]:
            latex = RelatedRatesGeometry(setup=setup).to_latex()
            assert latex.strip(), f"{setup} produced empty LaTeX"
            # All 5 sub-cases ship real TikZ — no \fbox fallback.
            assert r"\begin{tikzpicture}" in latex
            assert r"\end{tikzpicture}" in latex
