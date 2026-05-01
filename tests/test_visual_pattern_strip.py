"""γ.4s — Tests for the K1 :class:`PatternStrip` visual primitive.

Covers:
- Default cells render to a parseable SVG envelope.
- Glyph cells emit SVG glyph elements (circle / rect / polygon / path).
- Text and number cells emit ``<text>`` elements.
- Missing (``None``) cells render with a "?" and a different fill.
- Determinism (same args → byte-identical SVG).
- ``to_text()`` lists cells in order with correct title.
- ``to_latex()`` produces a non-empty ``tikzpicture`` envelope.
- Edge cases: empty cells list, very long cells list (auto-resize).
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from src.visuals.figures.pattern_strip import PatternStrip


SVG_NS = "{http://www.w3.org/2000/svg}"


def _parse(svg: str) -> ET.Element:
    """Parse an SVG string — raises if malformed."""
    return ET.fromstring(svg)


# ---------------------------------------------------------------------------
# Basic rendering
# ---------------------------------------------------------------------------

class TestRendering:
    def test_default_cells_render(self):
        # Smoke test: a typical ABAB? pattern parses into a valid SVG.
        p = PatternStrip(cells=["apples", "books", "apples", "books", None])
        svg = p.to_svg()
        elem = _parse(svg)
        # 5 cells = 5 background rects (some glyphs add their own rect,
        # so we assert "at least" 5).
        rects = elem.findall(f".//{SVG_NS}rect")
        assert len(rects) >= 5

    def test_glyph_cells_produce_glyph_elements(self):
        # apples → circle, books → rounded_rect, stars → polygon (star),
        # hearts → path. All four shape primitives should be present.
        p = PatternStrip(cells=["apples", "books", "stars", "hearts"])
        elem = _parse(p.to_svg())
        assert len(elem.findall(f".//{SVG_NS}circle")) >= 1  # apples
        # 4 background rects + 1 from rounded_rect (books) = ≥5
        assert len(elem.findall(f".//{SVG_NS}rect")) >= 5
        assert len(elem.findall(f".//{SVG_NS}polygon")) >= 1  # star
        assert len(elem.findall(f".//{SVG_NS}path")) >= 1  # heart

    def test_text_and_number_cells_produce_text_elements(self):
        p = PatternStrip(cells=[2, 4, 6, "red", "blue"])
        elem = _parse(p.to_svg())
        texts = elem.findall(f".//{SVG_NS}text")
        # 5 cells → 5 text elements (no missing, no glyph).
        assert len(texts) == 5
        # Verify content order is preserved.
        contents = [t.text for t in texts]
        assert contents == ["2", "4", "6", "red", "blue"]

    def test_missing_cell_renders_question_mark(self):
        p = PatternStrip(cells=[2, 4, None, 8, 10])
        svg = p.to_svg()
        elem = _parse(svg)
        texts = elem.findall(f".//{SVG_NS}text")
        text_contents = [t.text for t in texts]
        # Order preserved: "2", "4", "?", "8", "10"
        assert text_contents == ["2", "4", "?", "8", "10"]

    def test_missing_cell_uses_different_fill(self):
        p = PatternStrip(
            cells=["apples", None],
            cell_fill="#dbeafe",
            missing_fill="#fde68a",
        )
        svg = p.to_svg()
        # Both fills should appear in the output.
        assert "#dbeafe" in svg
        assert "#fde68a" in svg


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------

class TestDeterminism:
    def test_same_inputs_byte_identical(self):
        a = PatternStrip(cells=["apples", "books", None, 4]).to_svg()
        b = PatternStrip(cells=["apples", "books", None, 4]).to_svg()
        assert a == b

    def test_different_cells_differ(self):
        a = PatternStrip(cells=["apples", "books"]).to_svg()
        b = PatternStrip(cells=["apples", "stars"]).to_svg()
        assert a != b


# ---------------------------------------------------------------------------
# to_text
# ---------------------------------------------------------------------------

class TestToText:
    def test_pattern_strip_with_glyphs_and_missing(self):
        p = PatternStrip(cells=["apples", "books", "apples", "books", None])
        assert p.to_text() == "Shape strip: apples, books, apples, books, ?."

    def test_number_strip_title(self):
        p = PatternStrip(cells=[2, 4, None, 8, 10])
        assert p.to_text() == "Number strip: 2, 4, ?, 8, 10."

    def test_shape_strip_no_missing(self):
        p = PatternStrip(cells=["square", "square", "square", "heart"])
        # "square" is not in the glyph map (we have "triangle" / "heart"
        # / etc but not "square"); falls through to text. Mixed text +
        # glyph → "Pattern strip".
        text = p.to_text()
        assert "square, square, square, heart" in text

    def test_pure_glyph_strip_says_shape(self):
        # All four cells are glyph items, no missing → "Shape strip".
        p = PatternStrip(cells=["apples", "books", "stars", "hearts"])
        assert p.to_text().startswith("Shape strip:")

    def test_empty_cells_does_not_crash(self):
        p = PatternStrip(cells=[])
        assert "empty" in p.to_text().lower()


# ---------------------------------------------------------------------------
# to_latex
# ---------------------------------------------------------------------------

class TestToLatex:
    def test_returns_tikzpicture_envelope(self):
        latex = PatternStrip(cells=["apples", "books", None]).to_latex()
        assert latex.startswith(r"\begin{tikzpicture}")
        assert latex.endswith(r"\end{tikzpicture}")
        # Non-empty — should have at least one \draw command.
        assert r"\draw" in latex

    def test_missing_cell_uses_question_mark(self):
        latex = PatternStrip(cells=[2, None, 4]).to_latex()
        assert "{?}" in latex
        # Numeric cells appear as themselves.
        assert "{2}" in latex
        assert "{4}" in latex

    def test_empty_cells_returns_empty_tikz(self):
        latex = PatternStrip(cells=[]).to_latex()
        # Should still wrap in a valid envelope, even if no body.
        assert latex.startswith(r"\begin{tikzpicture}")
        assert latex.endswith(r"\end{tikzpicture}")
        assert r"\draw" not in latex


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_empty_cells_does_not_crash(self):
        p = PatternStrip(cells=[])
        # Should produce a parseable empty SVG envelope.
        elem = _parse(p.to_svg())
        # No content elements — viewport rect only.
        assert elem.tag.endswith("svg")

    def test_none_cells_argument_treated_as_empty(self):
        p = PatternStrip(cells=None)
        assert p.cells == []
        # Still produces a valid (empty) SVG.
        _parse(p.to_svg())

    def test_long_cell_list_auto_resizes(self):
        # 20 cells × 48 = 960 px, but viewport is only 480 px. The
        # builder should shrink cell_size so the strip fits.
        cells = list(range(1, 21))
        p = PatternStrip(cells=cells, cell_size=48, width=480)
        # Cell size should have shrunk below the requested 48.
        assert p.cell_size < 48
        # Total strip width should fit inside (width - 2*margin).
        assert p.cell_size * len(cells) <= p.width - 2 * p._MARGIN + 0.5
        # Output is still a valid SVG.
        _parse(p.to_svg())

    def test_short_cell_list_keeps_requested_size(self):
        # 3 cells × 48 = 144 px ≪ 480 viewport — no shrinking.
        p = PatternStrip(cells=["apples", "books", None], cell_size=48, width=480)
        assert p.cell_size == 48

    def test_unknown_string_renders_as_text(self):
        # "widget" isn't in the glyph map → falls to text rendering.
        p = PatternStrip(cells=["widget"])
        elem = _parse(p.to_svg())
        texts = elem.findall(f".//{SVG_NS}text")
        assert len(texts) == 1
        assert texts[0].text == "widget"
