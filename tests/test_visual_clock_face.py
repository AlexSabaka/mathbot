"""Smoke tests for :class:`ClockFace` (γ.4s K1 visual primitive).

Covers the multi-format contract (SVG / text / TikZ), the geometric
correctness of hand directions (the 12-o'clock-vs-+x-axis offset is
the easiest thing to break), input validation + rollover edge cases,
and determinism. The shared visual fixture suite
(``tests/test_visual.py``) stays untouched — these focus on the new
builder.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from src.visuals.figures.clock_face import ClockFace


SVG_NS = "{http://www.w3.org/2000/svg}"


def _parse(svg: str) -> ET.Element:
    """Parse an SVG string, failing the test cleanly if malformed."""
    try:
        return ET.fromstring(svg)
    except ET.ParseError as exc:  # pragma: no cover — diagnostic only
        pytest.fail(f"ClockFace produced invalid XML: {exc}\n---\n{svg}")


def _hand_endpoints(fig: ClockFace) -> list[tuple[float, float, float, float]]:
    """Return ``(x1, y1, x2, y2)`` for every ``<line>`` in the SVG.

    Hand-direction tests inspect the longest two lines in the SVG
    (after subtracting the ticks) — but since lines all share a common
    centre (the pivot), it's simpler to filter by "starts at the centre"
    and read off the endpoint.
    """
    root = _parse(fig.to_svg())
    out: list[tuple[float, float, float, float]] = []
    for line in root.iter(f"{SVG_NS}line"):
        x1 = float(line.get("x1", "0"))
        y1 = float(line.get("y1", "0"))
        x2 = float(line.get("x2", "0"))
        y2 = float(line.get("y2", "0"))
        out.append((x1, y1, x2, y2))
    return out


def _hands_only(fig: ClockFace) -> list[tuple[float, float, float, float]]:
    """Lines whose start point is the SVG centre — the two hands."""
    cx, cy = fig.width / 2, fig.height / 2
    return [
        (x1, y1, x2, y2)
        for (x1, y1, x2, y2) in _hand_endpoints(fig)
        if abs(x1 - cx) < 1e-6 and abs(y1 - cy) < 1e-6
    ]


class TestClockFaceSVG:
    def test_default_render_is_well_formed(self):
        """ClockFace(3) renders parseable SVG and ``render() == to_svg()``."""
        fig = ClockFace(hour=3)
        svg = fig.to_svg()
        root = _parse(svg)
        assert root.tag == f"{SVG_NS}svg"
        assert fig.render() == svg

    def test_svg_contains_twelve_hour_numerals(self):
        """Every numeral 1-12 appears as a ``<text>`` element."""
        fig = ClockFace(hour=3)
        root = _parse(fig.to_svg())
        texts = {t.text for t in root.iter(f"{SVG_NS}text")}
        for n in range(1, 13):
            assert str(n) in texts, f"numeral {n} missing from clock face"

    def test_minute_marks_disabled(self):
        """``show_minute_marks=False`` → only the 12 hour ticks remain.

        Hand count is fixed at 2, so total ``<line>`` count drops to 14
        (12 ticks + 2 hands). With minute marks on we'd see 14 + 48
        non-overlapping minute ticks = 62.
        """
        on = ClockFace(hour=3, show_minute_marks=True)
        off = ClockFace(hour=3, show_minute_marks=False)
        on_lines = len(_hand_endpoints(on))
        off_lines = len(_hand_endpoints(off))
        assert off_lines == 14, f"expected 12 hour ticks + 2 hands, got {off_lines}"
        assert on_lines > off_lines, "minute marks should add lines"

    def test_determinism(self):
        """Same inputs → identical bytes."""
        a = ClockFace(hour=7, minute=30).to_svg()
        b = ClockFace(hour=7, minute=30).to_svg()
        assert a == b


class TestClockFaceHandDirections:
    """Hand-angle correctness — guards the clock→math 90° offset.

    The easy bug is to forget that clock 0° points *up* (the 12) while
    polar 0° points *right* (the 3). Each test asserts a hand endpoint
    sits in the expected quadrant relative to the centre.
    """

    def test_hour_hand_at_3_points_right(self):
        fig = ClockFace(hour=3, minute=0)
        cx, cy = fig.width / 2, fig.height / 2
        hands = _hands_only(fig)
        # Hour hand is the shorter of the two — pick by length.
        hands_sorted = sorted(
            hands,
            key=lambda L: (L[2] - L[0]) ** 2 + (L[3] - L[1]) ** 2,
        )
        hour_hand = hands_sorted[0]
        # Endpoint should lie on the +x axis: x > cx, y ≈ cy.
        assert hour_hand[2] > cx, "hour hand at 3:00 should point right"
        assert abs(hour_hand[3] - cy) < 1e-3, "hour hand at 3:00 should be horizontal"

    def test_hour_hand_at_6_points_down(self):
        fig = ClockFace(hour=6, minute=0)
        cx, cy = fig.width / 2, fig.height / 2
        hands = _hands_only(fig)
        hands_sorted = sorted(
            hands,
            key=lambda L: (L[2] - L[0]) ** 2 + (L[3] - L[1]) ** 2,
        )
        hour_hand = hands_sorted[0]
        # SVG y-down: "down" means y > cy.
        assert hour_hand[3] > cy, "hour hand at 6:00 should point down (SVG y-down)"
        assert abs(hour_hand[2] - cx) < 1e-3, "hour hand at 6:00 should be vertical"

    def test_hour_hand_at_12_points_up(self):
        fig = ClockFace(hour=12, minute=0)
        cx, cy = fig.width / 2, fig.height / 2
        hands = _hands_only(fig)
        hands_sorted = sorted(
            hands,
            key=lambda L: (L[2] - L[0]) ** 2 + (L[3] - L[1]) ** 2,
        )
        hour_hand = hands_sorted[0]
        # SVG y-down: "up" means y < cy.
        assert hour_hand[3] < cy, "hour hand at 12:00 should point up (SVG y-down)"
        assert abs(hour_hand[2] - cx) < 1e-3, "hour hand at 12:00 should be vertical"

    def test_minute_hand_at_00_points_up(self):
        fig = ClockFace(hour=3, minute=0)
        cx, cy = fig.width / 2, fig.height / 2
        hands = _hands_only(fig)
        hands_sorted = sorted(
            hands,
            key=lambda L: (L[2] - L[0]) ** 2 + (L[3] - L[1]) ** 2,
        )
        minute_hand = hands_sorted[-1]  # longer one
        assert minute_hand[3] < cy, "minute hand at :00 should point up"
        assert abs(minute_hand[2] - cx) < 1e-3, "minute hand at :00 should be vertical"

    def test_minute_hand_at_30_points_down(self):
        fig = ClockFace(hour=3, minute=30)
        cx, cy = fig.width / 2, fig.height / 2
        hands = _hands_only(fig)
        hands_sorted = sorted(
            hands,
            key=lambda L: (L[2] - L[0]) ** 2 + (L[3] - L[1]) ** 2,
        )
        minute_hand = hands_sorted[-1]
        assert minute_hand[3] > cy, "minute hand at :30 should point down"
        assert abs(minute_hand[2] - cx) < 1e-3, "minute hand at :30 should be vertical"

    def test_minute_hand_at_15_points_right(self):
        fig = ClockFace(hour=3, minute=15)
        cx, cy = fig.width / 2, fig.height / 2
        hands = _hands_only(fig)
        hands_sorted = sorted(
            hands,
            key=lambda L: (L[2] - L[0]) ** 2 + (L[3] - L[1]) ** 2,
        )
        minute_hand = hands_sorted[-1]
        assert minute_hand[2] > cx, "minute hand at :15 should point right"
        assert abs(minute_hand[3] - cy) < 1e-3, "minute hand at :15 should be horizontal"


class TestClockFaceEdgeCases:
    def test_hour_zero_rolls_to_twelve(self):
        """``hour=0`` → canonicalised to 12 (midnight/noon convention)."""
        fig = ClockFace(hour=0, minute=0)
        assert fig.hour == 12
        assert "12:00" in fig.to_text()

    def test_hour_thirteen_rolls_to_one(self):
        """``hour=13`` → 13 mod 12 == 1."""
        fig = ClockFace(hour=13, minute=0)
        assert fig.hour == 1
        assert "1:00" in fig.to_text()

    def test_minute_sixty_rolls_to_next_hour(self):
        """``minute=60`` bumps hour and zeroes minute."""
        fig = ClockFace(hour=3, minute=60)
        assert fig.hour == 4
        assert fig.minute == 0

    def test_minute_sixty_at_twelve_wraps(self):
        """The hour-rollover from minute=60 still respects mod-12 wrap."""
        # hour=12, minute=60 → hour=13 → mod 12 = 1.
        fig = ClockFace(hour=12, minute=60)
        assert fig.hour == 1
        assert fig.minute == 0

    def test_negative_hour_rejected(self):
        with pytest.raises(ValueError):
            ClockFace(hour=-1, minute=0)

    def test_negative_minute_rejected(self):
        with pytest.raises(ValueError):
            ClockFace(hour=3, minute=-5)

    def test_minute_over_sixty_rejected(self):
        """``minute=61`` is suspicious (likely minute-of-day) — reject."""
        with pytest.raises(ValueError):
            ClockFace(hour=3, minute=61)

    def test_invalid_radius_rejected(self):
        with pytest.raises(ValueError):
            ClockFace(hour=3, radius=0)


class TestClockFaceText:
    def test_to_text_format_simple(self):
        """``Clock showing 3:00.`` — minutes zero-padded."""
        assert ClockFace(hour=3, minute=0).to_text() == "Clock showing 3:00."

    def test_to_text_format_half_past(self):
        assert ClockFace(hour=7, minute=30).to_text() == "Clock showing 7:30."

    def test_to_text_format_quarter_past_twelve(self):
        assert ClockFace(hour=12, minute=15).to_text() == "Clock showing 12:15."


class TestClockFaceLatex:
    def test_to_latex_uses_tikz(self):
        latex = ClockFace(hour=3).to_latex()
        assert r"\begin{tikzpicture}" in latex
        assert r"\end{tikzpicture}" in latex

    def test_to_latex_has_twelve_numeral_nodes(self):
        """Twelve ``\\node`` entries — one per hour numeral.

        Counting raw ``\\node`` occurrences works because ClockFace
        only uses nodes for numerals; ticks and hands use ``\\draw``.
        """
        latex = ClockFace(hour=3).to_latex()
        assert latex.count(r"\node") == 12

    def test_to_latex_emits_circle_and_hands(self):
        """One ``\\draw circle`` for the face, plus per-hand ``\\draw`` lines."""
        latex = ClockFace(hour=3).to_latex()
        assert r"\draw[thick] (0,0) circle" in latex
        # Two hand lines from the centre.
        assert latex.count(r"(0,0) -- (") >= 2
