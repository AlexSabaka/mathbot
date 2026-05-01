"""γ.4s — Tests for :class:`BalanceScale` (K1 measurement.weight visual).

Covers the multi-format contract (SVG / text / TikZ), tilt math
(left-heavy → left-down, right-heavy → right-down, equal → level),
the ``show_balance=False`` override, glyph counts per pan,
empty-pan handling, determinism, the heavier-side text outcome,
and constructor validation for negative inputs.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from src.visuals.figures.balance_scale import BalanceScale


SVG_NS = "{http://www.w3.org/2000/svg}"


def _parse(svg: str) -> ET.Element:
    """Parse an SVG string and return the root element.

    Raises a clearly-flagged failure if the SVG is malformed — XML
    parse errors here mean we've broken the SVG envelope.
    """
    try:
        return ET.fromstring(svg)
    except ET.ParseError as exc:  # pragma: no cover — diagnostic only
        pytest.fail(f"BalanceScale produced invalid XML: {exc}\n---\n{svg}")


class TestBalanceScaleSVG:
    def test_default_render_well_formed(self):
        fig = BalanceScale(3, 5, item="blocks")
        svg = fig.to_svg()
        root = _parse(svg)
        assert root.tag == f"{SVG_NS}svg"
        # render() returns the same as to_svg().
        assert fig.render() == svg

    def test_left_heavier_tilts_left_down(self):
        # left_count > right_count → left end of beam should sit at a
        # *larger* SVG y (further down) than the right end.
        fig = BalanceScale(left_count=6, right_count=2, item="blocks")
        left_end, right_end = fig._beam_endpoints()
        assert left_end[1] > right_end[1], (
            "left-heavier should tilt the left pan down "
            f"(left y={left_end[1]}, right y={right_end[1]})"
        )

    def test_right_heavier_tilts_right_down(self):
        fig = BalanceScale(left_count=1, right_count=4, item="blocks")
        left_end, right_end = fig._beam_endpoints()
        assert right_end[1] > left_end[1], (
            "right-heavier should tilt the right pan down "
            f"(left y={left_end[1]}, right y={right_end[1]})"
        )

    def test_equal_counts_render_level(self):
        # Both ends share the same y on a level beam.
        fig = BalanceScale(left_count=3, right_count=3, item="apples")
        left_end, right_end = fig._beam_endpoints()
        assert left_end[1] == pytest.approx(right_end[1], abs=1e-6)

    def test_show_balance_false_keeps_beam_level(self):
        # With show_balance=False the beam stays level even when the
        # counts differ.
        fig = BalanceScale(
            left_count=6, right_count=1, item="books", show_balance=False
        )
        left_end, right_end = fig._beam_endpoints()
        assert left_end[1] == pytest.approx(right_end[1], abs=1e-6)

    def test_pan_glyph_counts_match_inputs(self):
        # Each glyph maps to exactly one SVG element. Items are
        # circles for "apples" → count <circle> elements that aren't
        # the pivot dot. Easier: assert (left + right + extras) where
        # extras are the post / base / pivot. Use the stacking helper
        # directly to keep the test resilient to extra static glyphs.
        fig = BalanceScale(left_count=3, right_count=5, item="apples")
        # The stacking helper is the source of truth for glyph count.
        left = fig._stack_positions(3, fig._pan_centre(fig._beam_endpoints()[0]))
        right = fig._stack_positions(5, fig._pan_centre(fig._beam_endpoints()[1]))
        assert len(left) == 3
        assert len(right) == 5

        # End-to-end: count circles in the SVG. "apples" → circle
        # glyphs (each = 1 <circle>). The pivot dot adds 1.
        svg = fig.to_svg()
        root = _parse(svg)
        circles = list(root.iter(f"{SVG_NS}circle"))
        # 3 + 5 glyphs + 1 pivot dot = 9.
        assert len(circles) == 9

    def test_left_pan_empty_renders_no_left_glyphs(self):
        fig = BalanceScale(left_count=0, right_count=4, item="blocks")
        # Stacker returns no positions for count=0.
        left_positions = fig._stack_positions(
            0, fig._pan_centre(fig._beam_endpoints()[0])
        )
        assert left_positions == []
        # Right pan still populated.
        right_positions = fig._stack_positions(
            4, fig._pan_centre(fig._beam_endpoints()[1])
        )
        assert len(right_positions) == 4
        # Empty pan still tilts (left empty → right is heavier → right down).
        left_end, right_end = fig._beam_endpoints()
        assert right_end[1] > left_end[1]

    def test_determinism(self):
        # Same inputs → byte-identical SVG. Required for the
        # fixture-drift lint to behave sanely on K1 templates.
        a = BalanceScale(3, 5, item="blocks").to_svg()
        b = BalanceScale(3, 5, item="blocks").to_svg()
        assert a == b


class TestBalanceScaleText:
    def test_left_heavier_text(self):
        text = BalanceScale(6, 2, item="books").to_text()
        assert "6 books" in text
        assert "2 books" in text
        assert "Left side heavier" in text

    def test_right_heavier_text(self):
        text = BalanceScale(3, 5, item="blocks").to_text()
        assert "3 blocks" in text
        assert "5 blocks" in text
        assert "Right side heavier" in text

    def test_balanced_text(self):
        text = BalanceScale(4, 4, item="marbles").to_text()
        assert "4 marbles" in text
        assert "balanced" in text.lower()

    def test_show_balance_false_text_does_not_reveal(self):
        text = BalanceScale(
            6, 1, item="apples", show_balance=False
        ).to_text()
        # Heavier-side phrase suppressed.
        assert "Left side heavier" not in text
        assert "Right side heavier" not in text


class TestBalanceScaleLatex:
    def test_to_latex_non_empty(self):
        latex = BalanceScale(3, 5, item="blocks").to_latex()
        assert latex.startswith(r"\begin{tikzpicture}")
        assert latex.endswith(r"\end{tikzpicture}")
        # Tilt scope present for unequal counts.
        assert "rotate around" in latex

    def test_to_latex_escapes_item(self):
        # Item with a LaTeX-reserved character should round-trip safely.
        latex = BalanceScale(2, 2, item="cards & coins").to_latex()
        # Unescaped & in TikZ would break the build; escaped form
        # appears as \&.
        assert r"\&" in latex


class TestBalanceScaleValidation:
    def test_negative_left_raises(self):
        with pytest.raises(ValueError):
            BalanceScale(left_count=-1, right_count=2)

    def test_negative_right_raises(self):
        with pytest.raises(ValueError):
            BalanceScale(left_count=2, right_count=-1)

    def test_zero_counts_render(self):
        # Both pans empty → level beam, no glyphs, just the apparatus.
        fig = BalanceScale(0, 0, item="blocks")
        svg = fig.to_svg()
        root = _parse(svg)
        # Only the pivot dot circle should be present (no glyphs).
        circles = list(root.iter(f"{SVG_NS}circle"))
        assert len(circles) == 1
