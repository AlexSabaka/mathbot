"""Function plot builder for Approach-B visuals.

Handles single- or multi-curve function plots with an axis frame,
optional gridlines, point markers, horizontal asymptotes, and a
title. Built for K12 calculus visuals — the curve sampler skips
points where `f(x)` raises (1/0, sqrt of negative, etc.) so a plot
of `1/x` over `(-2, 2)` doesn't dump the entire SVG when it hits
the singularity.
"""

from __future__ import annotations

from typing import Callable, List, Optional, Tuple

from .base import DEFAULT_FONT, SVGBuilder, _esc, _fmt


class PlotSVG(SVGBuilder):
    """Build a 2D function plot.

    Usage::

        plot = PlotSVG(width=400, height=300, x_range=(-3, 3), title="y = x²")
        plot.plot(lambda x: x**2)
        plot.point(1, 1, label="(1, 1)")
        Visual = plot.render()

    Coordinate model: data-space (`x`, `y`) is translated to SVG
    pixel-space at render time via the auto-fit y-range (defaulted to
    `[min(y), max(y)]` of the sampled curves, with 5% padding).
    """

    def __init__(
        self,
        width: int = 400,
        height: int = 300,
        x_range: Tuple[float, float] = (-10.0, 10.0),
        y_range: Optional[Tuple[float, float]] = None,
        title: Optional[str] = None,
        gridlines: bool = True,
        round_to: Optional[int] = None,
    ):
        super().__init__(width, height)
        self.x_min, self.x_max = float(x_range[0]), float(x_range[1])
        self.y_range_explicit = y_range
        self.title = title
        self.gridlines = gridlines
        # γ.4q (Q.1). When set, auto-fitted y-range bounds snap to the
        # nearest multiple of `round_to` (floor for the lower bound,
        # ceil for the upper). Cooling-style plots that auto-fit to
        # `(18.x, 93.x)` from data round to `(10, 100)` with `round_to=10`,
        # eliminating the rubric item-12 axis-artifact failure. Default
        # None preserves the legacy 5%-padding behaviour. Ignored when
        # `y_range` is supplied explicitly (the caller is in control).
        self.round_to = round_to
        self._curves: List[Tuple[List[float], List[Optional[float]], Optional[str]]] = []
        self._points: List[Tuple[float, float, Optional[str]]] = []
        self._hlines: List[Tuple[float, Optional[str]]] = []
        # Reserve viewport margins for axis labels and title.
        self._margin_l = 40
        self._margin_r = 12
        self._margin_t = 28 if title else 12
        self._margin_b = 28

    # ----- public authoring API ---------------------------------------

    def plot(
        self,
        f: Callable[[float], float],
        label: Optional[str] = None,
        n: int = 200,
    ) -> "PlotSVG":
        """Sample `f` at `n` points across `x_range` and queue a curve.

        `f(x)` may raise — those points become breaks in the polyline,
        so a plot of `tan` doesn't connect across asymptotes with a
        spurious vertical line.
        """
        if n < 2:
            n = 2
        step = (self.x_max - self.x_min) / (n - 1)
        xs: List[float] = []
        ys: List[Optional[float]] = []
        for i in range(n):
            x = self.x_min + i * step
            try:
                y = float(f(x))
                if y != y or abs(y) == float("inf"):  # NaN / inf
                    y = None  # type: ignore[assignment]
            except Exception:
                y = None  # type: ignore[assignment]
            xs.append(x)
            ys.append(y)
        self._curves.append((xs, ys, label))
        return self

    def point(self, x: float, y: float, label: Optional[str] = None) -> "PlotSVG":
        """Mark a single point with optional label."""
        self._points.append((float(x), float(y), label))
        return self

    def horizontal_line(self, y: float, label: Optional[str] = None) -> "PlotSVG":
        """Draw a horizontal asymptote / threshold line at y=value."""
        self._hlines.append((float(y), label))
        return self

    # ----- rendering --------------------------------------------------

    def _data_to_svg(self, x: float, y: float, y_min: float, y_max: float) -> Tuple[float, float]:
        plot_w = self.width - self._margin_l - self._margin_r
        plot_h = self.height - self._margin_t - self._margin_b
        sx = self._margin_l + (x - self.x_min) / (self.x_max - self.x_min) * plot_w
        # SVG y axis points down; flip so larger y plots higher.
        sy = self._margin_t + (y_max - y) / (y_max - y_min) * plot_h
        return sx, sy

    def _autofit_y(self) -> Tuple[float, float]:
        if self.y_range_explicit is not None:
            return float(self.y_range_explicit[0]), float(self.y_range_explicit[1])
        finite_ys: List[float] = []
        for _xs, ys, _label in self._curves:
            finite_ys.extend(y for y in ys if y is not None)
        for _y, _label in self._hlines:
            finite_ys.append(_y)
        for _x, y, _label in self._points:
            finite_ys.append(y)
        if not finite_ys:
            return -1.0, 1.0
        lo, hi = min(finite_ys), max(finite_ys)
        if lo == hi:
            lo -= 1.0
            hi += 1.0
        pad = (hi - lo) * 0.05
        lo, hi = lo - pad, hi + pad
        if self.round_to:
            import math
            r = self.round_to
            lo = math.floor(lo / r) * r
            hi = math.ceil(hi / r) * r
            if lo == hi:
                hi += r
        return lo, hi

    def render(self) -> str:
        y_min, y_max = self._autofit_y()
        parts: List[str] = []

        # Plot rectangle frame
        plot_w = self.width - self._margin_l - self._margin_r
        plot_h = self.height - self._margin_t - self._margin_b
        parts.append(
            f'<rect x="{self._margin_l}" y="{self._margin_t}" '
            f'width="{plot_w}" height="{plot_h}" fill="white" stroke="#333" stroke-width="1"/>'
        )

        # Optional title
        if self.title:
            parts.append(
                f'<text x="{self.width / 2}" y="18" text-anchor="middle" '
                f'{DEFAULT_FONT}>{_esc(self.title)}</text>'
            )

        # Gridlines: 5 evenly spaced verticals + 5 horizontals.
        if self.gridlines:
            for i in range(1, 5):
                gx = self._margin_l + i / 5 * plot_w
                parts.append(
                    f'<line x1="{_fmt(gx)}" y1="{self._margin_t}" '
                    f'x2="{_fmt(gx)}" y2="{self._margin_t + plot_h}" '
                    f'stroke="#eee" stroke-width="1"/>'
                )
                gy = self._margin_t + i / 5 * plot_h
                parts.append(
                    f'<line x1="{self._margin_l}" y1="{_fmt(gy)}" '
                    f'x2="{self._margin_l + plot_w}" y2="{_fmt(gy)}" '
                    f'stroke="#eee" stroke-width="1"/>'
                )

        # Zero axes (if visible)
        if self.x_min < 0 < self.x_max:
            zx, _ = self._data_to_svg(0, y_min, y_min, y_max)
            parts.append(
                f'<line x1="{_fmt(zx)}" y1="{self._margin_t}" '
                f'x2="{_fmt(zx)}" y2="{self._margin_t + plot_h}" '
                f'stroke="#999" stroke-width="1"/>'
            )
        if y_min < 0 < y_max:
            _, zy = self._data_to_svg(self.x_min, 0, y_min, y_max)
            parts.append(
                f'<line x1="{self._margin_l}" y1="{_fmt(zy)}" '
                f'x2="{self._margin_l + plot_w}" y2="{_fmt(zy)}" '
                f'stroke="#999" stroke-width="1"/>'
            )

        # Axis range labels (corner ticks only — keep legible without crowding).
        parts.append(
            f'<text x="{self._margin_l - 4}" y="{self._margin_t + plot_h + 14}" '
            f'text-anchor="end" {DEFAULT_FONT}>{_fmt(self.x_min)}</text>'
        )
        parts.append(
            f'<text x="{self._margin_l + plot_w}" y="{self._margin_t + plot_h + 14}" '
            f'text-anchor="end" {DEFAULT_FONT}>{_fmt(self.x_max)}</text>'
        )
        parts.append(
            f'<text x="{self._margin_l - 4}" y="{self._margin_t + 4}" '
            f'text-anchor="end" {DEFAULT_FONT}>{_fmt(y_max)}</text>'
        )
        parts.append(
            f'<text x="{self._margin_l - 4}" y="{self._margin_t + plot_h}" '
            f'text-anchor="end" {DEFAULT_FONT}>{_fmt(y_min)}</text>'
        )

        # Horizontal asymptote / threshold lines.
        for y, label in self._hlines:
            _, sy = self._data_to_svg(self.x_min, y, y_min, y_max)
            parts.append(
                f'<line x1="{self._margin_l}" y1="{_fmt(sy)}" '
                f'x2="{self._margin_l + plot_w}" y2="{_fmt(sy)}" '
                f'stroke="#c33" stroke-width="1" stroke-dasharray="4 3"/>'
            )
            if label:
                parts.append(
                    f'<text x="{self._margin_l + plot_w - 4}" y="{_fmt(sy - 4)}" '
                    f'text-anchor="end" fill="#c33" {DEFAULT_FONT}>{_esc(label)}</text>'
                )

        # Curves — emit each contiguous-finite run as its own polyline so
        # singularities break the visual line cleanly.
        curve_colors = ["#1f77b4", "#d62728", "#2ca02c", "#9467bd", "#ff7f0e"]
        for idx, (xs, ys, label) in enumerate(self._curves):
            color = curve_colors[idx % len(curve_colors)]
            run: List[str] = []
            for x, y in zip(xs, ys):
                if y is None:
                    if run:
                        parts.append(
                            f'<polyline fill="none" stroke="{color}" '
                            f'stroke-width="1.6" points="{" ".join(run)}"/>'
                        )
                        run = []
                    continue
                sx, sy = self._data_to_svg(x, y, y_min, y_max)
                if self._margin_t <= sy <= self._margin_t + plot_h:
                    run.append(f"{_fmt(sx)},{_fmt(sy)}")
                else:
                    if run:
                        parts.append(
                            f'<polyline fill="none" stroke="{color}" '
                            f'stroke-width="1.6" points="{" ".join(run)}"/>'
                        )
                        run = []
            if run:
                parts.append(
                    f'<polyline fill="none" stroke="{color}" '
                    f'stroke-width="1.6" points="{" ".join(run)}"/>'
                )
            if label:
                # Label anchors at the right end of the curve. γ.4q
                # (Q.1) clip-prevention: when the rightward label would
                # run past the canvas (curves whose last point lands
                # in the right margin band — Newton's-cooling plot
                # was the canonical "T" rendered as a single clipped
                # glyph), flip to text-anchor=end and place the label
                # *inside* the canvas trailing the line endpoint. The
                # vertical nudge (-4) lifts the inside-anchored label
                # above the line so it doesn't sit on top of it.
                last_finite = next(
                    ((x, y) for x, y in reversed(list(zip(xs, ys))) if y is not None),
                    None,
                )
                if last_finite is not None:
                    sx, sy = self._data_to_svg(last_finite[0], last_finite[1], y_min, y_max)
                    # Approx label pixel width (8 px / char serif). Bias
                    # high so a marginal call still flips inward.
                    label_w = max(len(label) * 8 + 4, 16)
                    if sx + 4 + label_w > self.width - 2:
                        parts.append(
                            f'<text x="{_fmt(sx - 4)}" y="{_fmt(sy - 4)}" '
                            f'text-anchor="end" fill="{color}" {DEFAULT_FONT}>'
                            f'{_esc(label)}</text>'
                        )
                    else:
                        parts.append(
                            f'<text x="{_fmt(sx + 4)}" y="{_fmt(sy)}" fill="{color}" '
                            f'{DEFAULT_FONT}>{_esc(label)}</text>'
                        )

        # Marked points.
        for x, y, label in self._points:
            sx, sy = self._data_to_svg(x, y, y_min, y_max)
            parts.append(
                f'<circle cx="{_fmt(sx)}" cy="{_fmt(sy)}" r="3" fill="#222"/>'
            )
            if label:
                parts.append(
                    f'<text x="{_fmt(sx + 6)}" y="{_fmt(sy - 4)}" {DEFAULT_FONT}>{_esc(label)}</text>'
                )

        return self._wrap(*parts)
