"""Smoke tests for :class:`ObjectArray` (γ.4s K1 visual primitive).

Covers the multi-format contract (SVG / text / TikZ), determinism,
the four layout modes (plain / grouped / strikes / comparison), and
the edge cases that live at the K1 boundary (count=0, count=1).
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from src.visuals.figures.object_array import ObjectArray


SVG_NS = "{http://www.w3.org/2000/svg}"


def _parse(svg: str) -> ET.Element:
    """Parse an SVG string and return the root element."""
    try:
        return ET.fromstring(svg)
    except ET.ParseError as exc:  # pragma: no cover — diagnostic only
        pytest.fail(f"ObjectArray produced invalid XML: {exc}\n---\n{svg}")


def _glyph_count(root: ET.Element) -> int:
    """Count primitive glyph elements (circle / rect / polygon / path).

    Matches the union of glyph forms shape_glyph emits. Strike <line>
    elements are excluded so callers can assert glyph counts cleanly.
    """
    return (
        len(list(root.iter(f"{SVG_NS}circle")))
        + len(list(root.iter(f"{SVG_NS}rect")))
        + len(list(root.iter(f"{SVG_NS}polygon")))
        + len(list(root.iter(f"{SVG_NS}path")))
    )


class TestObjectArraySVG:
    def test_default_render_is_well_formed(self):
        fig = ObjectArray()
        svg = fig.to_svg()
        root = _parse(svg)
        assert root.tag == f"{SVG_NS}svg"
        # render() must mirror to_svg().
        assert fig.render() == svg

    def test_count_5_produces_5_glyphs(self):
        fig = ObjectArray(count=5, item="apples")
        root = _parse(fig.to_svg())
        # apples → circle glyphs; no strikes/groups so glyph count == 5.
        assert _glyph_count(root) == 5

    def test_groups_produce_visible_gap(self):
        # groups=[3, 2]: positions 2→3 should be wider than 0→1.
        fig = ObjectArray(count=5, item="dots", groups=[3, 2])
        positions = fig._grouped_positions()
        normal_gap = positions[1] - positions[0]
        group_gap = positions[3] - positions[2]
        assert group_gap > normal_gap, (
            f"group break gap ({group_gap}) should exceed normal gap "
            f"({normal_gap})"
        )

    def test_strikes_produce_line_elements(self):
        fig = ObjectArray(count=5, item="apples", strikes=[3, 4])
        root = _parse(fig.to_svg())
        lines = list(root.iter(f"{SVG_NS}line"))
        # Two diagonal lines per strike → 4 line elements for 2 strikes.
        assert len(lines) == 4
        # Strikes must be red.
        assert all(line.get("stroke") == "#dc2626" for line in lines)

    def test_comparison_produces_two_rows(self):
        fig = ObjectArray(comparison=(8, 5), item="dots")
        root = _parse(fig.to_svg())
        # 8 + 5 = 13 glyphs total.
        assert _glyph_count(root) == 13
        # Glyphs split across two y-coordinates (top + bottom rows).
        ys = {c.get("cy") for c in root.iter(f"{SVG_NS}circle")}
        assert len(ys) == 2, f"expected exactly two row y-coords, got {ys}"

    def test_item_routing_apples_is_circles(self):
        # apples → circle (round-item bucket in shape_glyph).
        fig = ObjectArray(count=3, item="apples")
        root = _parse(fig.to_svg())
        circles = list(root.iter(f"{SVG_NS}circle"))
        rects = list(root.iter(f"{SVG_NS}rect"))
        assert len(circles) == 3
        assert len(rects) == 0

    def test_item_routing_books_is_rects(self):
        # books → rounded_rect (book/box/block bucket in shape_glyph).
        fig = ObjectArray(count=3, item="books")
        root = _parse(fig.to_svg())
        circles = list(root.iter(f"{SVG_NS}circle"))
        rects = list(root.iter(f"{SVG_NS}rect"))
        assert len(rects) == 3
        assert len(circles) == 0

    def test_determinism(self):
        # Same inputs → byte-identical SVG. Lint's fixture-drift check
        # depends on this property project-wide.
        a = ObjectArray(count=5, item="apples", groups=[3, 2], strikes=[4]).to_svg()
        b = ObjectArray(count=5, item="apples", groups=[3, 2], strikes=[4]).to_svg()
        assert a == b


class TestObjectArrayEdgeCases:
    def test_count_zero_is_valid(self):
        fig = ObjectArray(count=0, item="apples")
        svg = fig.to_svg()
        root = _parse(svg)
        # Empty array — no glyphs, but the SVG envelope is still valid.
        assert _glyph_count(root) == 0
        assert root.tag == f"{SVG_NS}svg"

    def test_count_one_renders_centered(self):
        fig = ObjectArray(count=1, item="apples")
        root = _parse(fig.to_svg())
        circles = list(root.iter(f"{SVG_NS}circle"))
        assert len(circles) == 1
        # Single item should sit at horizontal midpoint.
        cx = float(circles[0].get("cx"))
        assert abs(cx - fig.width / 2) < 0.5

    def test_comparison_auto_bumps_height(self):
        # Default height (80) is below the comparison minimum (160).
        fig = ObjectArray(comparison=(3, 2))
        assert fig.height >= 160

    def test_groups_must_sum_to_count(self):
        with pytest.raises(ValueError):
            ObjectArray(count=5, groups=[3, 3])

    def test_negative_count_rejected(self):
        with pytest.raises(ValueError):
            ObjectArray(count=-1)

    def test_strikes_out_of_range_silently_ignored(self):
        # Author passes a slightly-wrong strikes list; render shouldn't
        # break — out-of-range entries are dropped.
        fig = ObjectArray(count=3, item="apples", strikes=[2, 99])
        root = _parse(fig.to_svg())
        lines = list(root.iter(f"{SVG_NS}line"))
        # Only the in-range strike (index 2) is drawn → 2 diagonal lines.
        assert len(lines) == 2

    def test_unknown_item_falls_back_to_circle(self):
        # glyph_for falls back to circle for unknown items; the row
        # render path must follow suit (no exception).
        fig = ObjectArray(count=2, item="widgets")
        root = _parse(fig.to_svg())
        assert len(list(root.iter(f"{SVG_NS}circle"))) == 2


class TestObjectArrayText:
    def test_to_text_mentions_count_and_item(self):
        text = ObjectArray(count=5, item="apples").to_text()
        assert "5" in text
        assert "apples" in text

    def test_to_text_groups_phrasing(self):
        text = ObjectArray(count=8, item="apples", groups=[5, 3]).to_text()
        assert "5" in text and "3" in text
        assert "grouped" in text.lower()

    def test_to_text_comparison_phrasing(self):
        text = ObjectArray(comparison=(8, 5), item="dots").to_text()
        assert "comparison" in text.lower() or "Comparison" in text
        assert "8" in text and "5" in text
        assert "top" in text.lower() and "bottom" in text.lower()

    def test_to_text_strikes_phrasing(self):
        text = ObjectArray(count=8, item="apples", strikes=[5, 6, 7]).to_text()
        # Trailing strikes should produce the "last N" prose form.
        assert "last 3" in text
        assert "crossed out" in text


class TestObjectArrayLatex:
    def test_to_latex_uses_tikz_for_row(self):
        latex = ObjectArray(count=5, item="apples").to_latex()
        assert r"\begin{tikzpicture}" in latex
        assert r"\end{tikzpicture}" in latex
        # Five circles for a row of apples.
        assert latex.count("circle") >= 5

    def test_to_latex_emits_strike_strokes(self):
        latex = ObjectArray(count=5, item="apples", strikes=[4]).to_latex()
        # Strike lines reference the red colour and a thick stroke.
        assert "red" in latex
        # Two diagonal draws per strike.
        assert latex.count(r"\draw[red") >= 2

    def test_to_latex_falls_back_to_fbox_for_comparison(self):
        latex = ObjectArray(comparison=(8, 5), item="dots").to_latex()
        # Comparison mode opts into the fbox fallback per the contract.
        assert r"\fbox" in latex
        assert "8" in latex and "5" in latex

    def test_to_latex_books_uses_rectangle(self):
        latex = ObjectArray(count=2, item="books").to_latex()
        # rounded_rect → ``rectangle`` TikZ primitive.
        assert "rectangle" in latex
