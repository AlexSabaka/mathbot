"""γ.4s S.1 — Tests for the K1 ShapeGlyph helper.

Covers the six geometric primitives + the prose-item dispatcher.
Glyphs are tiny SVG snippets; tests assert (a) well-formedness when
embedded in an SVG envelope, (b) the expected element type for each
primitive, (c) deterministic output for fixed inputs, (d) the
dispatcher's case-insensitive lookup + safe fallback.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from src.visuals.figures.shape_glyph import (
    circle, rounded_rect, triangle, star, heart, dot, glyph_for,
)


def _parses_in_envelope(snippet: str) -> ET.Element:
    """Wrap a glyph snippet in `<svg>` and parse — confirms the snippet
    is a well-formed SVG fragment without producing a parse error."""
    wrapped = (
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'width="100" height="100" viewBox="0 0 100 100">'
        + snippet +
        '</svg>'
    )
    return ET.fromstring(wrapped)


# ---------------------------------------------------------------------------
# Primitive shapes
# ---------------------------------------------------------------------------

class TestPrimitives:
    def test_circle_renders_circle_element(self):
        snippet = circle(50, 50, 20, "#fb923c")
        elem = _parses_in_envelope(snippet)
        circles = elem.findall(".//{http://www.w3.org/2000/svg}circle")
        assert len(circles) == 1
        assert circles[0].get("fill") == "#fb923c"
        # diameter=20 → r=10
        assert circles[0].get("r") == "10"

    def test_rounded_rect_has_corner_radius(self):
        snippet = rounded_rect(50, 50, 30, "#60a5fa")
        elem = _parses_in_envelope(snippet)
        rects = elem.findall(".//{http://www.w3.org/2000/svg}rect")
        assert len(rects) == 1
        assert rects[0].get("rx") is not None
        assert float(rects[0].get("rx")) > 0
        # Width 30, height ≈ 25 (1.2:1 aspect)
        assert float(rects[0].get("width")) == 30
        assert float(rects[0].get("height")) == pytest.approx(24.9, abs=0.5)

    def test_triangle_has_three_vertices(self):
        snippet = triangle(50, 50, 20, "#34d399")
        elem = _parses_in_envelope(snippet)
        polys = elem.findall(".//{http://www.w3.org/2000/svg}polygon")
        assert len(polys) == 1
        # points string has 3 vertices = 3 "x,y" tokens
        points = polys[0].get("points").split()
        assert len(points) == 3

    def test_star_has_ten_vertices(self):
        snippet = star(50, 50, 20, "#facc15")
        elem = _parses_in_envelope(snippet)
        polys = elem.findall(".//{http://www.w3.org/2000/svg}polygon")
        assert len(polys) == 1
        # 5-pointed star = 10 alternating outer/inner vertices
        points = polys[0].get("points").split()
        assert len(points) == 10

    def test_heart_renders_path(self):
        snippet = heart(50, 50, 24, "#f472b6")
        elem = _parses_in_envelope(snippet)
        paths = elem.findall(".//{http://www.w3.org/2000/svg}path")
        assert len(paths) == 1
        d = paths[0].get("d")
        # Heart uses two cubic-bezier curves: should contain "C"
        assert "C" in d
        assert d.endswith("Z")

    def test_dot_is_smaller_than_circle(self):
        # Dot at size 20 should render smaller than circle at size 20.
        c_snippet = circle(50, 50, 20, "#000")
        d_snippet = dot(50, 50, 20, "#000")
        c_elem = _parses_in_envelope(c_snippet)
        d_elem = _parses_in_envelope(d_snippet)
        c_r = float(c_elem.find(".//{http://www.w3.org/2000/svg}circle").get("r"))
        d_r = float(d_elem.find(".//{http://www.w3.org/2000/svg}circle").get("r"))
        assert d_r < c_r


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------

class TestDeterminism:
    def test_same_inputs_byte_identical(self):
        for fn in (circle, rounded_rect, triangle, star, heart, dot):
            a = fn(40, 40, 18, "#ccc")
            b = fn(40, 40, 18, "#ccc")
            assert a == b

    def test_different_positions_differ(self):
        a = circle(40, 40, 18, "#ccc")
        b = circle(50, 40, 18, "#ccc")
        assert a != b


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

class TestGlyphFor:
    def test_apple_maps_to_circle(self):
        assert glyph_for("apple") is circle
        assert glyph_for("apples") is circle

    def test_book_maps_to_rounded_rect(self):
        assert glyph_for("book") is rounded_rect
        assert glyph_for("books") is rounded_rect

    def test_star_maps_to_star(self):
        assert glyph_for("star") is star
        assert glyph_for("stars") is star

    def test_heart_maps_to_heart(self):
        assert glyph_for("heart") is heart

    def test_case_insensitive(self):
        assert glyph_for("APPLES") is circle
        assert glyph_for("Books") is rounded_rect

    def test_strips_whitespace(self):
        assert glyph_for("  apples  ") is circle

    def test_unknown_item_falls_back_to_circle(self):
        assert glyph_for("widget") is circle
        assert glyph_for("xyzzy") is circle
        # Empty string falls back too — never raises.
        assert glyph_for("") is circle

    def test_dispatcher_output_renders(self):
        # End-to-end: pick glyph via dispatcher, render, parse.
        for item in ("apples", "books", "stars", "hearts", "blocks", "unknown"):
            g = glyph_for(item)
            snippet = g(50, 50, 20, "#888")
            _parses_in_envelope(snippet)  # raises if malformed
