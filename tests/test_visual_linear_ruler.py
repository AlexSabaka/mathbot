"""Smoke tests for :class:`LinearRuler` (γ.4s — K1 measurement).

Covers the multi-format contract (SVG / text / TikZ), the layout
invariant (object-bar width = N × unit_size; left edges flush), the
unit-item dispatch (cubes → glyph rounded-rect, clips → pill, other
→ plain square), determinism, and the two interesting edge cases
(zero-length object; very large counts shrinking unit_size to fit).
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

import pytest

from src.visuals.figures.linear_ruler import LinearRuler


SVG_NS = "{http://www.w3.org/2000/svg}"


def _parse(svg: str) -> ET.Element:
    """Parse SVG; fail loudly if malformed."""
    try:
        return ET.fromstring(svg)
    except ET.ParseError as exc:  # pragma: no cover — diagnostic only
        pytest.fail(f"LinearRuler produced invalid XML: {exc}\n---\n{svg}")


def _all_rects(root: ET.Element) -> list[ET.Element]:
    return list(root.iter(f"{SVG_NS}rect"))


def _all_circles(root: ET.Element) -> list[ET.Element]:
    return list(root.iter(f"{SVG_NS}circle"))


class TestLinearRulerSVG:
    def test_basic_render_is_well_formed(self):
        fig = LinearRuler(object_length_units=5, unit_item="cubes",
                          object_label="eraser")
        svg = fig.to_svg()
        root = _parse(svg)
        assert root.tag == f"{SVG_NS}svg"
        # render() must equal to_svg() — keystone contract.
        assert fig.render() == svg

    def test_unit_cell_count_matches_input(self):
        # `cubes` dispatches to glyph_for(rounded_rect), so each unit
        # cell is a <rect>. The object bar is also a <rect>, so the
        # total rect count is N + 1.
        fig = LinearRuler(object_length_units=8, unit_item="cubes",
                          object_label="eraser")
        root = _parse(fig.to_svg())
        rects = _all_rects(root)
        # 8 cubes (rounded-rect glyphs) + 1 object bar = 9 rects.
        assert len(rects) == 8 + 1

    def test_object_bar_width_equals_n_times_unit_size(self):
        """Layout invariant: bar width == N * unit_size (within tol)."""
        fig = LinearRuler(object_length_units=5, unit_item="cubes",
                          object_label="eraser")
        root = _parse(fig.to_svg())
        rects = _all_rects(root)
        # The bar is the rect with object_color fill.
        bar = next(
            r for r in rects if r.get("fill") == fig.object_color
        )
        bar_w = float(bar.get("width"))
        expected = fig.object_length_units * fig.unit_size
        # _fmt rounds to 2 decimal places, so allow a 0.01 tolerance.
        assert abs(bar_w - expected) < 0.02

    def test_object_bar_left_edge_aligns_with_unit_row(self):
        """Critical alignment: bar's x equals first cell's left edge.

        We can't introspect "first cell" cleanly because cubes render
        as glyphs (rounded_rect with x=cx-w/2). Reconstruct the unit
        row's left edge from `_strip_origin_x` and verify the bar
        starts there.
        """
        fig = LinearRuler(object_length_units=6, unit_item="cubes",
                          object_label="eraser")
        root = _parse(fig.to_svg())
        bar = next(
            r for r in _all_rects(root) if r.get("fill") == fig.object_color
        )
        bar_x = float(bar.get("x"))
        # _fmt rounds to 2 decimals; allow 0.02 tolerance.
        assert abs(bar_x - fig._strip_origin_x()) < 0.02

    def test_cubes_produce_glyph_rounded_rects(self):
        # rounded_rect glyph emits <rect rx="..."> (rounded corners).
        fig = LinearRuler(object_length_units=4, unit_item="cubes",
                          object_label="eraser")
        root = _parse(fig.to_svg())
        rects = _all_rects(root)
        # Filter to non-bar rects (i.e. exclude the object_color one).
        unit_rects = [
            r for r in rects if r.get("fill") != fig.object_color
        ]
        assert len(unit_rects) == 4
        # Every unit rect should carry an rx attribute (rounded corners).
        assert all(r.get("rx") is not None for r in unit_rects)

    def test_clips_produce_pill_shape(self):
        # Pill: rect with rx=ry=h/2 (full-height rounding) and the
        # configured unit_color fill (no glyph dispatch — clips aren't
        # in _GLYPH_MAP).
        fig = LinearRuler(object_length_units=5, unit_item="clips",
                          object_label="pencil")
        root = _parse(fig.to_svg())
        unit_rects = [
            r for r in _all_rects(root) if r.get("fill") == fig.unit_color
        ]
        assert len(unit_rects) == 5
        # Pills are wider than tall (clip silhouette).
        for r in unit_rects:
            w = float(r.get("width"))
            h = float(r.get("height"))
            assert w > h, f"clip pill should be wider than tall, got w={w} h={h}"
            # rx ≈ h/2 → fully rounded ends. _fmt's 2-decimal
            # truncation means we allow 0.02 of slop.
            rx = float(r.get("rx"))
            assert abs(rx - h / 2) < 0.02

    def test_object_label_appears_in_svg(self):
        fig = LinearRuler(object_length_units=5, unit_item="cubes",
                          object_label="eraser")
        svg = fig.to_svg()
        assert "eraser" in svg
        root = _parse(svg)
        texts = [t.text for t in root.iter(f"{SVG_NS}text")]
        assert "eraser" in texts

    def test_zero_length_does_not_crash(self):
        fig = LinearRuler(object_length_units=0, unit_item="cubes",
                          object_label="eraser")
        svg = fig.to_svg()
        root = _parse(svg)
        # No unit cells, but the bar nub is still emitted.
        rects = _all_rects(root)
        # Just the object-bar nub (no glyph cubes).
        unit_rects = [r for r in rects if r.get("fill") != fig.object_color]
        assert len(unit_rects) == 0

    def test_large_count_shrinks_unit_size_to_fit(self):
        # With 20 cells in a 480px viewport, unit_size must drop below
        # the default to keep the strip inside the viewport.
        fig = LinearRuler(object_length_units=20, unit_item="cubes",
                          object_label="stick")
        # Check that 20 * unit_size ≤ width - 2 * margin.
        total = fig.unit_size * fig.object_length_units
        assert total <= fig.width - 2 * fig._MARGIN + 1e-6

    def test_determinism(self):
        # Same args → byte-identical SVG. The fixture-drift lint
        # depends on this; cover it here so regressions surface fast.
        a = LinearRuler(object_length_units=6, unit_item="cubes",
                        object_label="eraser").to_svg()
        b = LinearRuler(object_length_units=6, unit_item="cubes",
                        object_label="eraser").to_svg()
        assert a == b


class TestLinearRulerText:
    def test_to_text_mentions_label_and_count(self):
        text = LinearRuler(object_length_units=8, unit_item="cubes",
                           object_label="eraser").to_text()
        assert "eraser" in text
        assert "8" in text
        assert "cubes" in text

    def test_to_text_handles_clips(self):
        text = LinearRuler(object_length_units=5, unit_item="clips",
                           object_label="pencil").to_text()
        assert "pencil" in text
        assert "5" in text
        assert "clips" in text

    def test_to_text_zero_length_flagged(self):
        text = LinearRuler(object_length_units=0, unit_item="cubes",
                           object_label="eraser").to_text()
        # Spec: zero-length must surface in the text fallback.
        assert "0" in text
        assert "eraser" in text


class TestLinearRulerLatex:
    def test_to_latex_uses_tikz(self):
        latex = LinearRuler(object_length_units=5, unit_item="cubes",
                            object_label="eraser").to_latex()
        assert r"\begin{tikzpicture}" in latex
        assert r"\end{tikzpicture}" in latex
        # Real TikZ — guards against a silent regression to fbox.
        assert r"\draw" in latex

    def test_to_latex_emits_n_unit_rectangles_plus_bar(self):
        latex = LinearRuler(object_length_units=4, unit_item="cubes",
                            object_label="eraser").to_latex()
        # 4 unit rectangles + 1 object bar = 5 rectangle draws.
        assert latex.count("rectangle") == 4 + 1

    def test_to_latex_includes_object_label(self):
        latex = LinearRuler(object_length_units=3, unit_item="clips",
                            object_label="pencil").to_latex()
        assert "pencil" in latex


class TestLinearRulerEdgeCases:
    def test_negative_object_length_rejected(self):
        with pytest.raises(ValueError):
            LinearRuler(object_length_units=-1, unit_item="cubes",
                        object_label="eraser")

    def test_unknown_unit_item_falls_back_to_square(self):
        # "widgets" isn't in _GLYPH_MAP and isn't a clip → plain square.
        fig = LinearRuler(object_length_units=3, unit_item="widgets",
                          object_label="stick")
        root = _parse(fig.to_svg())
        unit_rects = [
            r for r in _all_rects(root) if r.get("fill") == fig.unit_color
        ]
        # 3 plain-square cells; each rect must NOT have rx (no rounding).
        assert len(unit_rects) == 3
        for r in unit_rects:
            assert r.get("rx") is None
