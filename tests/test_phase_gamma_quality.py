"""Phase γ.4q (quality pass) unit tests.

Q.1 builder additions:
  - ``PlotSVG(round_to=...)`` snaps auto-fitted y-bounds to round multiples.
  - ``PlotSVG`` curve-label clip prevention flips to inside-anchor when
    the right-end label would run off the canvas.
  - ``CircuitSVG(source_disconnected=True)`` renders the open-gap glyph
    instead of the default closed-circle source with `+`/`−` polarity.

Q.3 lint additions:
  - ``filler_boilerplate`` (info) — substring match against catalogue.
  - ``none_in_output`` (warning) — None / null / undefined / N/A literals.
  - ``axis_range_artifact`` extension for non-round integer labels,
    restricted to plot-shaped SVGs (those with ``<polyline>``).
"""

from __future__ import annotations

import math
import re
import xml.etree.ElementTree as ET

import pytest

from src.audit.findings import Finding
from src.audit.lint import (
    _is_axis_label_artifact,
    check_axis_range_artifact,
    check_filler_boilerplate,
    check_none_in_output,
)
from src.audit.render import RenderedSample
from src.visuals import CircuitSVG, PlotSVG
from src.yaml_loader import TemplateDefinition


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_template(**kwargs) -> TemplateDefinition:
    base = dict(
        id="t1", version="1.0.0", author="t", created="2026-04-29",
        grade=12, topic="calculus.integrals", family="integral_application",
        difficulty="medium", steps=4,
    )
    base.update(kwargs)
    return TemplateDefinition(**base)


def _sample(body: str = "P", answer: str = "0", tier: str = "easy") -> RenderedSample:
    return RenderedSample(
        template_id="t1", seed=1, tier=tier,
        body=body, answer=answer, raw={},
    )


# ---------------------------------------------------------------------------
# Q.1 PlotSVG — round_to
# ---------------------------------------------------------------------------

class TestPlotSVGRoundTo:
    def _y_corner_labels(self, plot: PlotSVG) -> list[str]:
        """Pull the y-axis corner labels (top + bottom) from rendered SVG."""
        svg = plot.render()
        # Y-axis corners are the only labels at x=margin_l-4 with text-anchor=end.
        # Match `>NN<` content that's purely numeric.
        return re.findall(r">(-?\d+(?:\.\d+)?)<", svg)

    def test_default_no_rounding(self):
        # Without round_to, autofit gives padded data range — non-round.
        plot = PlotSVG(width=300, height=180, x_range=(0, 30))
        plot.plot(lambda x: 23 + 66 * math.exp(-0.05 * x))
        labels = self._y_corner_labels(plot)
        # Pre-fix behaviour: bounds are (lo - pad, hi + pad) where lo/hi
        # are data extremes — typically non-multiples of 10.
        # Just verify the labels are floats (no rounding applied).
        assert any("." in v or int(v) % 10 != 0 for v in labels[2:4])

    def test_round_to_10(self):
        plot = PlotSVG(
            width=300, height=180, x_range=(0, 30), round_to=10,
        )
        plot.plot(lambda x: 23 + 66 * math.exp(-0.05 * x))
        labels = self._y_corner_labels(plot)
        # Y-axis corners are labels[2], labels[3] (after x_min, x_max).
        # Both should be multiples of 10.
        y_max, y_min = labels[2], labels[3]
        assert int(y_max) % 10 == 0, f"y_max {y_max} not multiple of 10"
        assert int(y_min) % 10 == 0, f"y_min {y_min} not multiple of 10"

    def test_round_to_5(self):
        plot = PlotSVG(
            width=300, height=180, x_range=(0, 10), round_to=5,
        )
        plot.plot(lambda x: x * 1.7 + 2)
        labels = self._y_corner_labels(plot)
        y_max, y_min = labels[2], labels[3]
        assert int(y_max) % 5 == 0
        assert int(y_min) % 5 == 0

    def test_explicit_y_range_overrides_round_to(self):
        # Authors who pass y_range= explicitly are in control;
        # round_to should not override.
        plot = PlotSVG(
            width=300, height=180, x_range=(0, 10),
            y_range=(0.5, 3.7), round_to=10,
        )
        plot.plot(lambda x: x * 0.3 + 1)
        labels = self._y_corner_labels(plot)
        # The explicit (0.5, 3.7) survives.
        y_max, y_min = labels[2], labels[3]
        assert "0.5" in y_min or float(y_min) == pytest.approx(0.5)
        assert "3.7" in y_max or float(y_max) == pytest.approx(3.7)


class TestPlotSVGLabelClipPrevention:
    def test_label_at_right_edge_flips_inside(self):
        # A line whose right end lands very close to the canvas edge.
        # The label "LongLabelName" would clip if rendered with
        # text-anchor=start at sx+4. Clip prevention flips it.
        plot = PlotSVG(width=200, height=120, x_range=(0, 1))
        plot.plot(lambda x: x, label="LongLabelName")
        svg = plot.render()
        # Look for the label text element. It must have text-anchor=end.
        m = re.search(
            r'<text[^>]*text-anchor="end"[^>]*>LongLabelName</text>', svg,
        )
        assert m is not None, "expected label flipped to text-anchor=end"

    def test_label_with_room_keeps_outside_anchor(self):
        # A curve whose finite range ends mid-canvas (the function
        # raises past x=0.5) so the right-end label attaches at a
        # mid-canvas sx, not at the right edge. With plenty of room
        # right of the endpoint, the label stays at text-anchor=start.
        def half_domain(x):
            if x > 0.5:
                raise ValueError("out of domain past 0.5")
            return x

        plot = PlotSVG(width=400, height=120, x_range=(0, 1))
        plot.plot(half_domain, label="f")
        svg = plot.render()
        m = re.search(r'<text[^>]*>f</text>', svg)
        assert m is not None
        # Mid-canvas anchor: no flip needed.
        assert 'text-anchor="end"' not in m.group(0)


# ---------------------------------------------------------------------------
# Q.1 CircuitSVG — source_disconnected
# ---------------------------------------------------------------------------

class TestCircuitSVGSourceDisconnected:
    def test_default_renders_closed_circle(self):
        ckt = CircuitSVG(R="R", L="L", C="C", V="12V")
        svg = ckt.render()
        assert "<circle" in svg
        assert ">+<" in svg
        # Unicode minus glyph
        assert ">−<" in svg

    def test_disconnected_omits_circle_and_polarity(self):
        ckt = CircuitSVG(
            R="R", L="L", C="C", V="",
            source_disconnected=True,
        )
        svg = ckt.render()
        # The source-position circle is gone.
        assert "<circle" not in svg
        # Polarity glyphs absent.
        assert ">+<" not in svg
        assert ">−<" not in svg

    def test_disconnected_renders_two_terminator_strokes(self):
        # The open-gap glyph is two short parallel strokes around
        # cy ± gap/2. Just check the SVG parses and contains additional
        # <line> elements vs the closed variant (since the source
        # gap adds 2 line elements + 2 wire stubs vs 2 wire stubs in
        # the closed variant).
        ckt_open = CircuitSVG(
            R="R", L="L", C="C", V="", source_disconnected=True,
        )
        svg = ckt_open.render()
        # Parses as XML
        ET.fromstring(svg)
        assert svg.count("<line") >= 4

    def test_v_label_still_renders_when_supplied(self):
        # An author who wants to keep a label on a disconnected source
        # can — V_label still emits when non-empty.
        ckt = CircuitSVG(
            R="R", L="L", C="C", V="V = 0",
            source_disconnected=True,
        )
        svg = ckt.render()
        assert ">V = 0<" in svg


# ---------------------------------------------------------------------------
# Q.3 axis_range_artifact (extended for integers)
# ---------------------------------------------------------------------------

class TestAxisRangeArtifactIntegerExtension:
    def _plot_svg(self, *labels: str) -> str:
        """Stub a plot-shaped SVG (with <polyline>) carrying the given labels."""
        text_elems = "".join(f"<text>{l}</text>" for l in labels)
        return f'<svg><polyline points="0,0 1,1"/>{text_elems}</svg>'

    def test_round_integer_bounds_ok(self):
        svg = self._plot_svg("0", "100", "50", "200")
        assert check_axis_range_artifact(svg, _make_template()) == []

    def test_non_round_integer_bound_fires(self):
        svg = self._plot_svg("0", "94", "100", "30")
        f = check_axis_range_artifact(svg, _make_template())
        assert len(f) == 1
        assert "94" in f[0].message

    def test_cooling_18_94_case(self):
        # The original cooling-template auto-fitted (18, 94) bounds
        # — the seed plan's canonical example.
        svg = self._plot_svg("0", "30", "94", "18")
        f = check_axis_range_artifact(svg, _make_template())
        assert len(f) == 1
        msg = f[0].message
        assert "18" in msg or "94" in msg

    def test_single_digit_integers_ok(self):
        # Counting axes routinely use 0, 1, 2, …, 9.
        svg = self._plot_svg("0", "1", "2", "3", "4", "5")
        assert check_axis_range_artifact(svg, _make_template()) == []

    def test_table_svg_skipped(self):
        # Tables don't have <polyline>, so the rule short-circuits and
        # the integer-extension doesn't fire on table cells like "17"
        # or "13" (Riemann's f(xᵢ) integer cells).
        svg = '<svg><rect/><text>17</text><text>13</text></svg>'
        assert check_axis_range_artifact(svg, _make_template()) == []

    def test_decimal_artifact_still_fires(self):
        # Decimal branch unchanged: ≥2 non-zero decimal digits flag.
        svg = self._plot_svg("0", "37.85")
        f = check_axis_range_artifact(svg, _make_template())
        assert len(f) == 1
        assert "37.85" in f[0].message

    def test_decimal_with_trailing_zero_ok(self):
        # "1.50" → trim → "1.5" → 1 digit → ok.
        svg = self._plot_svg("0", "1.50", "10.00")
        assert check_axis_range_artifact(svg, _make_template()) == []


class TestIsAxisLabelArtifactHelper:
    def test_decimals(self):
        assert _is_axis_label_artifact("1.5") is False
        assert _is_axis_label_artifact("1.50") is False
        assert _is_axis_label_artifact("37.85") is True

    def test_round_integers(self):
        assert _is_axis_label_artifact("0") is False
        assert _is_axis_label_artifact("5") is False
        assert _is_axis_label_artifact("100") is False
        assert _is_axis_label_artifact("250") is False
        assert _is_axis_label_artifact("1000") is False

    def test_non_round_integers(self):
        assert _is_axis_label_artifact("18") is True
        assert _is_axis_label_artifact("94") is True
        assert _is_axis_label_artifact("123") is True

    def test_negative_handling(self):
        # Sign doesn't change roundness.
        assert _is_axis_label_artifact("-100") is False
        assert _is_axis_label_artifact("-94") is True


# ---------------------------------------------------------------------------
# Q.3 filler_boilerplate
# ---------------------------------------------------------------------------

class TestFillerBoilerplate:
    def test_clean_prose_no_finding(self):
        s = _sample("How much did Maria pay?")
        assert check_filler_boilerplate(s, _make_template()) == []

    def test_please_solve_fires(self):
        s = _sample("How much did Maria pay? Please solve this problem.")
        f = check_filler_boilerplate(s, _make_template())
        assert len(f) == 1
        assert f[0].rule == "filler_boilerplate"
        assert f[0].severity == "info"

    def test_find_the_answer_fires(self):
        s = _sample("Compute x. Find the answer.")
        f = check_filler_boilerplate(s, _make_template())
        assert len(f) == 1

    def test_case_insensitive(self):
        s = _sample("PLEASE SOLVE THIS PROBLEM.")
        f = check_filler_boilerplate(s, _make_template())
        assert len(f) == 1


# ---------------------------------------------------------------------------
# Q.3 none_in_output
# ---------------------------------------------------------------------------

class TestNoneInOutput:
    def test_clean_no_finding(self):
        s = _sample(body="A clean problem.", answer="42")
        assert check_none_in_output(s, _make_template()) == []

    def test_none_in_answer_fires(self):
        s = _sample(body="Find x.", answer="None")
        f = check_none_in_output(s, _make_template())
        assert len(f) == 1
        assert f[0].rule == "none_in_output"
        assert f[0].severity == "warning"
        assert "None" in f[0].message

    def test_none_in_body_fires(self):
        s = _sample(body="The value is None for some reason.", answer="42")
        f = check_none_in_output(s, _make_template())
        assert len(f) == 1
        assert "body" in f[0].message

    def test_null_fires(self):
        s = _sample(body="Find x.", answer="null")
        f = check_none_in_output(s, _make_template())
        assert len(f) == 1

    def test_undefined_fires(self):
        s = _sample(body="x is undefined here.", answer="42")
        f = check_none_in_output(s, _make_template())
        assert len(f) == 1

    def test_anonymous_does_not_false_positive(self):
        # Word boundary: "Anonymous" contains "Non" but not "None" as
        # standalone token.
        s = _sample(body="Anonymous donated $5.", answer="5")
        assert check_none_in_output(s, _make_template()) == []

    def test_nullable_does_not_false_positive(self):
        s = _sample(body="The field is nullable in the schema.", answer="42")
        # "nullable" contains "null" but only as substring; word
        # boundary requires standalone token. "Nullable" → "ullable"
        # after "n" so the regex won't match a `\bnull\b` boundary
        # inside "nullable".
        assert check_none_in_output(s, _make_template()) == []
