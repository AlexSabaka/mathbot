"""γ.3 (A.2) — :class:`FunctionGraphFigure`: function plot + annotations.

Extends :class:`src.visuals.plot.PlotSVG` with the calculus-flavoured
annotation primitives K11–K12 templates lean on: tangent / secant
lines, area-under-curve shading, marked critical points, axis
intercepts, and dashed asymptote crosshairs. The base class
remains untouched — annotations layer on top of the queue-then-
render pipeline by mirroring :meth:`PlotSVG.render` and inserting
extra paint passes in the right z-order.

The companion :class:`AxesAnnotation` dataclass bundles intercepts,
asymptotes, and critical points together so a template can build a
pre-cooked annotation set in Python and apply it in one call rather
than firing six individual ``mark_*`` invocations.

Multi-format rendering follows the γ.3 keystone contract every
figure builder shares with :class:`src.visuals.table.TableSVG`:

- :meth:`to_svg` — self-contained SVG (also returned by :meth:`render`).
- :meth:`to_text` — plain-English description of plot + annotations.
- :meth:`to_latex` — minimal raw TikZ (``\\draw plot ...``) for the
  curve plus dashed/filled lines for annotations. Falls back to
  ``\\fbox{[Figure: ...]}`` only if the curve queue is empty.

Determinism: same constructor args + same enqueue order → byte-
identical SVG. All geometry resolves to floats formatted through
:func:`_fmt`, which strips trailing zeros so renderers don't shift
coordinate strings underneath us.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple

from ..base import DEFAULT_FONT, _esc, _fmt, _latex_escape
from ..plot import PlotSVG


# Colour palette for the new annotation paint passes. Kept as module
# constants so a downstream rebrand only needs to flip these values.
_TANGENT_STROKE = "#16a34a"      # green — tangent at a point
_SECANT_STROKE = "#7c3aed"       # purple — secant through two points
_CRITICAL_FILL = "#dc2626"       # red — critical point marker
_CRITICAL_GUIDE = "#dc2626"      # red — perpendicular guide to x-axis
_INTERCEPT_FILL = "#1d4ed8"      # blue — intercept marker
_ASYMPTOTE_STROKE = "#9333ea"    # purple — asymptote (dashed)
_SHADE_DEFAULT = "#dbeafe"       # pale blue default shade fill


class FunctionGraphFigure(PlotSVG):
    """Function plot with annotation primitives.

    Inherits the full :class:`PlotSVG` authoring API
    (:meth:`plot`, :meth:`point`, :meth:`horizontal_line`) and adds
    the annotation methods documented below.  The render pipeline
    mirrors :meth:`PlotSVG.render` so we can interleave new paint
    passes at the right layer (shading lives *under* the curves;
    tangents / secants / critical guides live *over* them).

    Parameters
    ----------
    width, height:
        SVG viewport dimensions.
    x_range:
        ``(x_min, x_max)`` data-space window.
    y_range:
        Optional explicit ``(y_min, y_max)`` window. When ``None``
        the y range auto-fits to the union of every queued y value
        across curves, points, asymptotes, intercepts, and tangent
        endpoints (so a tangent line never gets clipped because it
        peeks outside the auto-fitted range).
    title:
        Optional plot title.
    gridlines:
        Whether to draw the 5×5 background gridlines (inherited).
    round_to:
        Optional snap value for the auto-fitted y range (inherited).
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
        super().__init__(
            width=width,
            height=height,
            x_range=x_range,
            y_range=y_range,
            title=title,
            gridlines=gridlines,
            round_to=round_to,
        )
        # Annotation queues — order matters for determinism.
        self._tangents: List[Tuple[float, float, float, Optional[str]]] = []
        self._secants: List[Tuple[float, float, Optional[str]]] = []
        self._shaded_areas: List[Tuple[float, float, str]] = []
        self._intercepts: List[Tuple[str, float, Optional[str]]] = []
        self._criticals: List[Tuple[float, Optional[str]]] = []
        self._asymptotes: List[Tuple[str, float, Optional[str]]] = []

    # ------------------------------------------------------------------
    # Annotation authoring API
    # ------------------------------------------------------------------

    def tangent_at(
        self,
        x: float,
        slope: float,
        length: float = 2.0,
        label: Optional[str] = None,
    ) -> "FunctionGraphFigure":
        """Queue a tangent line of total data-units length ``length``.

        The line is centred on ``(x, f(x))`` where ``f`` is the most
        recently queued curve.  When no curve has been registered the
        tangent is drawn through ``(x, 0)`` instead — useful for
        annotations on a derivative diagram where the underlying
        function never gets plotted as a curve.
        """
        self._tangents.append((float(x), float(slope), float(length), label))
        return self

    def secant(
        self,
        x1: float,
        x2: float,
        label: Optional[str] = None,
    ) -> "FunctionGraphFigure":
        """Queue a secant line through ``(x1, f(x1))`` and ``(x2, f(x2))``."""
        self._secants.append((float(x1), float(x2), label))
        return self

    def shade_area(
        self,
        x1: float,
        x2: float,
        fill: str = _SHADE_DEFAULT,
    ) -> "FunctionGraphFigure":
        """Queue a shaded region between the curve and the x-axis on ``[x1, x2]``.

        The shading uses the most recently queued curve's sample.
        Calling this before :meth:`plot` is a no-op at render time
        (we silently skip — the point is to fail soft so partially
        authored templates still produce *some* visual).
        """
        self._shaded_areas.append((float(x1), float(x2), fill))
        return self

    def mark_intercept(
        self,
        axis: str,
        value: float,
        label: Optional[str] = None,
    ) -> "FunctionGraphFigure":
        """Mark an intercept on the named axis (``"x"`` or ``"y"``)."""
        a = str(axis).lower()
        if a not in ("x", "y"):
            raise ValueError(f"axis must be 'x' or 'y', got {axis!r}")
        self._intercepts.append((a, float(value), label))
        return self

    def mark_critical(
        self,
        x: float,
        label: Optional[str] = None,
    ) -> "FunctionGraphFigure":
        """Mark a critical point at ``x`` with a perpendicular guide to the x-axis."""
        self._criticals.append((float(x), label))
        return self

    def mark_asymptote(
        self,
        value: float,
        kind: str = "horizontal",
        label: Optional[str] = None,
    ) -> "FunctionGraphFigure":
        """Queue a dashed asymptote line (``"horizontal"`` or ``"vertical"``)."""
        k = str(kind).lower()
        if k not in ("horizontal", "vertical"):
            raise ValueError(
                f"kind must be 'horizontal' or 'vertical', got {kind!r}"
            )
        self._asymptotes.append((k, float(value), label))
        return self

    def add_axes_annotation(self, ann: "AxesAnnotation") -> "FunctionGraphFigure":
        """Apply an :class:`AxesAnnotation` bundle (delegates to ``ann.apply``)."""
        ann.apply(self)
        return self

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _latest_curve(self) -> Optional[Tuple[List[float], List[Optional[float]], Optional[str]]]:
        """Return the most recently queued curve, or ``None`` if no curves."""
        if not self._curves:
            return None
        return self._curves[-1]

    def _f_at(self, x: float) -> Optional[float]:
        """Linear-interpolate ``f(x)`` from the most recent curve's samples.

        We don't keep a reference to the original ``f`` callable — once
        :meth:`plot` queues a curve it's a list of sampled points.  This
        is enough for tangent / secant anchoring; if the requested ``x``
        falls in a sampled gap (a singularity) we return ``None`` and
        callers fall back to drawing through ``(x, 0)``.
        """
        curve = self._latest_curve()
        if curve is None:
            return None
        xs, ys, _label = curve
        if not xs:
            return None
        # Off-window: clip to the nearest endpoint.
        if x <= xs[0]:
            return ys[0]
        if x >= xs[-1]:
            return ys[-1]
        # Linear search is fine — sample count is O(200).
        for i in range(len(xs) - 1):
            x0, x1 = xs[i], xs[i + 1]
            if x0 <= x <= x1:
                y0, y1 = ys[i], ys[i + 1]
                if y0 is None or y1 is None:
                    return None
                if x1 == x0:
                    return y0
                t = (x - x0) / (x1 - x0)
                return y0 + t * (y1 - y0)
        return None

    def _annotation_ys(self) -> List[float]:
        """Y values introduced by annotations — fed into :meth:`_autofit_y`.

        Without this, a tangent / secant / asymptote whose endpoints sit
        outside the curve's sampled y-range gets silently clipped by
        the auto-fit window. We expand the window to include them.
        """
        ys: List[float] = []
        for x, slope, length, _label in self._tangents:
            mid_y = self._f_at(x)
            if mid_y is None:
                mid_y = 0.0
            half = length / 2.0
            ys.append(mid_y + slope * half)
            ys.append(mid_y - slope * half)
        for x1, x2, _label in self._secants:
            for xv in (x1, x2):
                yv = self._f_at(xv)
                if yv is not None:
                    ys.append(yv)
        for axis, value, _label in self._intercepts:
            if axis == "y":
                ys.append(value)
        for x, _label in self._criticals:
            yv = self._f_at(x)
            if yv is not None:
                ys.append(yv)
        for kind, value, _label in self._asymptotes:
            if kind == "horizontal":
                ys.append(value)
        return ys

    def _autofit_y(self) -> Tuple[float, float]:  # type: ignore[override]
        """Override: fold annotation y-values into the auto-fit calculation."""
        if self.y_range_explicit is not None:
            return float(self.y_range_explicit[0]), float(self.y_range_explicit[1])
        # Reuse parent's logic by temporarily padding _hlines with our
        # annotation ys, then restoring. Cheaper than copy-pasting the
        # whole autofit body and keeps the round_to / pad behaviour in
        # one place.
        extras = self._annotation_ys()
        if not extras:
            return super()._autofit_y()
        saved_hlines = list(self._hlines)
        try:
            self._hlines = saved_hlines + [(y, None) for y in extras]
            return super()._autofit_y()
        finally:
            self._hlines = saved_hlines

    # ------------------------------------------------------------------
    # to_svg — mirrors PlotSVG.render with annotation paint passes
    # ------------------------------------------------------------------

    def to_svg(self) -> str:
        y_min, y_max = self._autofit_y()
        plot_w = self.width - self._margin_l - self._margin_r
        plot_h = self.height - self._margin_t - self._margin_b
        parts: List[str] = []

        # 1. Plot frame
        parts.append(
            f'<rect x="{self._margin_l}" y="{self._margin_t}" '
            f'width="{plot_w}" height="{plot_h}" fill="white" stroke="#333" stroke-width="1"/>'
        )

        # 2. Title
        if self.title:
            parts.append(
                f'<text x="{self.width / 2}" y="18" text-anchor="middle" '
                f'{DEFAULT_FONT}>{_esc(self.title)}</text>'
            )

        # 3. Gridlines (background-most layer apart from frame).
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

        # 4. Zero axes.
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

        # 5. Corner ticks.
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

        # 6. Shaded areas — paint *under* the curves so the curve outline
        #    sits cleanly on top of the fill.
        for x1, x2, fill in self._shaded_areas:
            poly = self._build_shade_polygon(x1, x2, y_min, y_max)
            if poly:
                parts.append(
                    f'<polygon points="{poly}" fill="{fill}" '
                    f'stroke="none" fill-opacity="0.7"/>'
                )

        # 7. Horizontal asymptotes inherited from PlotSVG (kept under the
        #    curves like the parent class does).
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

        # 8. Asymptote annotations (horizontal *or* vertical) — dashed.
        for kind, value, label in self._asymptotes:
            if kind == "horizontal":
                _, sy = self._data_to_svg(self.x_min, value, y_min, y_max)
                parts.append(
                    f'<line x1="{self._margin_l}" y1="{_fmt(sy)}" '
                    f'x2="{self._margin_l + plot_w}" y2="{_fmt(sy)}" '
                    f'stroke="{_ASYMPTOTE_STROKE}" stroke-width="1.2" '
                    f'stroke-dasharray="6 4"/>'
                )
                if label:
                    parts.append(
                        f'<text x="{self._margin_l + plot_w - 4}" y="{_fmt(sy - 4)}" '
                        f'text-anchor="end" fill="{_ASYMPTOTE_STROKE}" '
                        f'{DEFAULT_FONT}>{_esc(label)}</text>'
                    )
            else:  # vertical
                sx, _ = self._data_to_svg(value, y_min, y_min, y_max)
                parts.append(
                    f'<line x1="{_fmt(sx)}" y1="{self._margin_t}" '
                    f'x2="{_fmt(sx)}" y2="{self._margin_t + plot_h}" '
                    f'stroke="{_ASYMPTOTE_STROKE}" stroke-width="1.2" '
                    f'stroke-dasharray="6 4"/>'
                )
                if label:
                    parts.append(
                        f'<text x="{_fmt(sx + 4)}" y="{_fmt(self._margin_t + 12)}" '
                        f'fill="{_ASYMPTOTE_STROKE}" {DEFAULT_FONT}>'
                        f'{_esc(label)}</text>'
                    )

        # 9. Curves — same paint pass as the parent class.
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
                last_finite = next(
                    ((x, y) for x, y in reversed(list(zip(xs, ys))) if y is not None),
                    None,
                )
                if last_finite is not None:
                    sx, sy = self._data_to_svg(last_finite[0], last_finite[1], y_min, y_max)
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

        # 10. Tangent lines — sit on top of curves so the tangent
        #     endpoint visually lands on the curve.
        for x, slope, length, label in self._tangents:
            mid_y = self._f_at(x)
            if mid_y is None:
                mid_y = 0.0
            half = length / 2.0
            x_a, y_a = x - half, mid_y - slope * half
            x_b, y_b = x + half, mid_y + slope * half
            sxa, sya = self._data_to_svg(x_a, y_a, y_min, y_max)
            sxb, syb = self._data_to_svg(x_b, y_b, y_min, y_max)
            parts.append(
                f'<line x1="{_fmt(sxa)}" y1="{_fmt(sya)}" '
                f'x2="{_fmt(sxb)}" y2="{_fmt(syb)}" '
                f'stroke="{_TANGENT_STROKE}" stroke-width="1.4"/>'
            )
            if label:
                parts.append(
                    f'<text x="{_fmt(sxb + 4)}" y="{_fmt(syb)}" '
                    f'fill="{_TANGENT_STROKE}" {DEFAULT_FONT}>'
                    f'{_esc(label)}</text>'
                )

        # 11. Secant lines.
        for x1, x2, label in self._secants:
            y1 = self._f_at(x1)
            y2 = self._f_at(x2)
            if y1 is None or y2 is None:
                continue
            sxa, sya = self._data_to_svg(x1, y1, y_min, y_max)
            sxb, syb = self._data_to_svg(x2, y2, y_min, y_max)
            parts.append(
                f'<line x1="{_fmt(sxa)}" y1="{_fmt(sya)}" '
                f'x2="{_fmt(sxb)}" y2="{_fmt(syb)}" '
                f'stroke="{_SECANT_STROKE}" stroke-width="1.4" '
                f'stroke-dasharray="2 2"/>'
            )
            if label:
                mx, my = (sxa + sxb) / 2, (sya + syb) / 2
                parts.append(
                    f'<text x="{_fmt(mx)}" y="{_fmt(my - 4)}" '
                    f'text-anchor="middle" fill="{_SECANT_STROKE}" '
                    f'{DEFAULT_FONT}>{_esc(label)}</text>'
                )

        # 12. Critical-point markers + perpendicular guides.
        for x, label in self._criticals:
            y = self._f_at(x)
            if y is None:
                y = 0.0
            sx, sy = self._data_to_svg(x, y, y_min, y_max)
            # Guide to x-axis (the y=0 baseline; if 0 isn't inside the
            # auto-fitted window, drop the guide all the way to the
            # bottom of the plot frame so the visual hint still reads).
            if y_min < 0 < y_max:
                _, base_y = self._data_to_svg(x, 0.0, y_min, y_max)
            else:
                base_y = self._margin_t + plot_h
            parts.append(
                f'<line x1="{_fmt(sx)}" y1="{_fmt(sy)}" '
                f'x2="{_fmt(sx)}" y2="{_fmt(base_y)}" '
                f'stroke="{_CRITICAL_GUIDE}" stroke-width="1" '
                f'stroke-dasharray="3 3"/>'
            )
            parts.append(
                f'<circle cx="{_fmt(sx)}" cy="{_fmt(sy)}" r="4" '
                f'fill="{_CRITICAL_FILL}"/>'
            )
            if label:
                parts.append(
                    f'<text x="{_fmt(sx + 6)}" y="{_fmt(sy - 6)}" '
                    f'fill="{_CRITICAL_FILL}" {DEFAULT_FONT}>{_esc(label)}</text>'
                )

        # 13. Intercept markers — small dots on the named axis.
        for axis, value, label in self._intercepts:
            if axis == "x":
                # Sit on y=0 baseline (or bottom edge if 0 is off-window).
                if y_min < 0 < y_max:
                    sx, sy = self._data_to_svg(value, 0.0, y_min, y_max)
                else:
                    sx, _ = self._data_to_svg(value, y_min, y_min, y_max)
                    sy = self._margin_t + plot_h
            else:  # y intercept
                if self.x_min < 0 < self.x_max:
                    sx, sy = self._data_to_svg(0.0, value, y_min, y_max)
                else:
                    _, sy = self._data_to_svg(self.x_min, value, y_min, y_max)
                    sx = self._margin_l
            parts.append(
                f'<circle cx="{_fmt(sx)}" cy="{_fmt(sy)}" r="3.5" '
                f'fill="{_INTERCEPT_FILL}"/>'
            )
            if label:
                parts.append(
                    f'<text x="{_fmt(sx + 6)}" y="{_fmt(sy - 6)}" '
                    f'fill="{_INTERCEPT_FILL}" {DEFAULT_FONT}>{_esc(label)}</text>'
                )

        # 14. Inherited points (queued via PlotSVG.point()) — render last
        #     so they overlay everything else.
        for x, y, label in self._points:
            sx, sy = self._data_to_svg(x, y, y_min, y_max)
            parts.append(
                f'<circle cx="{_fmt(sx)}" cy="{_fmt(sy)}" r="3" fill="#222"/>'
            )
            if label:
                parts.append(
                    f'<text x="{_fmt(sx + 6)}" y="{_fmt(sy - 4)}" '
                    f'{DEFAULT_FONT}>{_esc(label)}</text>'
                )

        return self._wrap(*parts)

    def _build_shade_polygon(
        self,
        x1: float,
        x2: float,
        y_min: float,
        y_max: float,
    ) -> str:
        """Build the SVG ``points`` attribute for a shade polygon.

        Walks the most recent curve's samples between ``x1`` and ``x2``
        (resampling endpoints via :meth:`_f_at`) and stitches the
        polygon ``(x1, 0) → curve → (x2, 0)``. Returns ``""`` if no
        curve has been queued or the interval is empty.
        """
        curve = self._latest_curve()
        if curve is None:
            return ""
        xs, ys, _label = curve
        if not xs:
            return ""
        if x1 > x2:
            x1, x2 = x2, x1

        # Baseline (y=0) anchor — clamped to y-window when 0 is off-screen
        # so the polygon stays inside the plot frame and renderers don't
        # draw its lower edge across the corner-tick text.
        baseline = 0.0
        if not (y_min <= baseline <= y_max):
            baseline = max(y_min, min(y_max, baseline))

        pts: List[Tuple[float, float]] = []
        # Left wall.
        y_left = self._f_at(x1)
        pts.append((x1, baseline))
        if y_left is not None:
            pts.append((x1, y_left))
        # Curve samples in (x1, x2).
        for x, y in zip(xs, ys):
            if y is None:
                continue
            if x1 < x < x2:
                pts.append((x, y))
        # Right wall.
        y_right = self._f_at(x2)
        if y_right is not None:
            pts.append((x2, y_right))
        pts.append((x2, baseline))

        if len(pts) < 3:
            return ""

        return " ".join(
            f"{_fmt(self._data_to_svg(px, py, y_min, y_max)[0])},"
            f"{_fmt(self._data_to_svg(px, py, y_min, y_max)[1])}"
            for px, py in pts
        )

    # ------------------------------------------------------------------
    # to_text
    # ------------------------------------------------------------------

    def to_text(self) -> str:
        """Plain-English description.

        Lists the curve(s) and every annotation in *queue order*
        (tangents, then secants, then shaded areas, intercepts,
        critical points, asymptotes). The downstream alt-text /
        screen-reader fallback uses this verbatim.
        """
        lines: List[str] = []
        title = self.title or "Function plot"
        if self._curves:
            curve_part = title
            xr = f"x ∈ [{_fmt(self.x_min)}, {_fmt(self.x_max)}]"
            lines.append(f"Plot of {curve_part} over {xr}.")
        else:
            lines.append(f"{title} (no curve plotted).")

        for x, slope, length, label in self._tangents:
            extra = f" labelled '{label}'" if label else ""
            lines.append(
                f"Tangent line at x = {_fmt(x)} with slope {_fmt(slope)}"
                f" (length {_fmt(length)}){extra}."
            )
        for x1, x2, label in self._secants:
            extra = f" labelled '{label}'" if label else ""
            lines.append(
                f"Secant line from x = {_fmt(x1)} to x = {_fmt(x2)}{extra}."
            )
        for x1, x2, _fill in self._shaded_areas:
            lo, hi = (x1, x2) if x1 <= x2 else (x2, x1)
            lines.append(
                f"Shaded area on [{_fmt(lo)}, {_fmt(hi)}]."
            )
        for axis, value, label in self._intercepts:
            extra = f" labelled '{label}'" if label else ""
            lines.append(
                f"Intercept on {axis}-axis at {_fmt(value)}{extra}."
            )
        for x, label in self._criticals:
            extra = f" ({label})" if label else ""
            lines.append(
                f"Marked critical point at x = {_fmt(x)}{extra}."
            )
        for kind, value, label in self._asymptotes:
            extra = f" labelled '{label}'" if label else ""
            if kind == "horizontal":
                lines.append(f"Horizontal asymptote at y = {_fmt(value)}{extra}.")
            else:
                lines.append(f"Vertical asymptote at x = {_fmt(value)}{extra}.")
        return " ".join(lines)

    # ------------------------------------------------------------------
    # to_latex
    # ------------------------------------------------------------------

    def to_latex(self) -> str:
        """Minimal raw TikZ rendering.

        Curves render with ``\\draw plot coordinates {...}``; tangents
        and secants are dashed lines; asymptotes use ``[dashed]``;
        shaded regions use ``\\fill[opacity=0.3]``. We always emit a
        TikZ ``tikzpicture`` env when there's at least one curve;
        if the figure has no curve at all, fall back to ``\\fbox``
        so the LaTeX still compiles.
        """
        if not self._curves:
            descr = _latex_escape(self.to_text())
            return rf"\fbox{{[Figure: {descr}]}}"

        # TikZ scaling: 20 SVG-units ≈ 1 cm matches the SectorFigure
        # convention. We then scale data-space directly so the curve
        # spans roughly the same printed footprint as the SVG.
        # Pick a scale so the x-range fits ~6 cm wide.
        x_span = self.x_max - self.x_min
        x_scale = 6.0 / x_span if x_span else 1.0
        y_min, y_max = self._autofit_y()
        y_span = y_max - y_min
        y_scale = 4.0 / y_span if y_span else 1.0

        def tx(x: float) -> str:
            return _fmt((x - self.x_min) * x_scale)

        def ty(y: float) -> str:
            return _fmt((y - y_min) * y_scale)

        lines: List[str] = []
        lines.append(r"\begin{tikzpicture}")
        if self.title:
            lines.append(
                rf"  \node[above] at ({tx((self.x_min + self.x_max)/2)},"
                rf"{ty(y_max)}) {{{_latex_escape(self.title)}}};"
            )
        # Bounding rectangle.
        lines.append(
            rf"  \draw ({tx(self.x_min)},{ty(y_min)}) rectangle "
            rf"({tx(self.x_max)},{ty(y_max)});"
        )

        # Shaded regions first (under curves).
        for x1, x2, _fill in self._shaded_areas:
            curve = self._latest_curve()
            if curve is None:
                continue
            xs, ys, _label = curve
            if not xs:
                continue
            lo, hi = (x1, x2) if x1 <= x2 else (x2, x1)
            pts: List[Tuple[float, float]] = [(lo, 0.0)]
            for x, y in zip(xs, ys):
                if y is None:
                    continue
                if lo < x < hi:
                    pts.append((x, y))
            pts.append((hi, 0.0))
            if len(pts) >= 3:
                coords = " -- ".join(f"({tx(px)},{ty(py)})" for px, py in pts)
                lines.append(rf"  \fill[blue!20, opacity=0.3] {coords} -- cycle;")

        # Curves.
        for xs, ys, _label in self._curves:
            coords = " ".join(
                f"({tx(x)},{ty(y)})"
                for x, y in zip(xs, ys)
                if y is not None
            )
            if coords:
                lines.append(rf"  \draw[blue, thick] plot coordinates {{{coords}}};")

        # Asymptotes.
        for kind, value, label in self._asymptotes:
            if kind == "horizontal":
                lines.append(
                    rf"  \draw[dashed] ({tx(self.x_min)},{ty(value)}) -- "
                    rf"({tx(self.x_max)},{ty(value)});"
                )
            else:
                lines.append(
                    rf"  \draw[dashed] ({tx(value)},{ty(y_min)}) -- "
                    rf"({tx(value)},{ty(y_max)});"
                )
            if label:
                lines.append(
                    rf"  \node[right] at ({tx(self.x_max)},"
                    rf"{ty(value) if kind == 'horizontal' else ty(y_max)}) "
                    rf"{{{_latex_escape(label)}}};"
                )

        # Tangents.
        for x, slope, length, label in self._tangents:
            mid_y = self._f_at(x)
            if mid_y is None:
                mid_y = 0.0
            half = length / 2.0
            x_a, y_a = x - half, mid_y - slope * half
            x_b, y_b = x + half, mid_y + slope * half
            lines.append(
                rf"  \draw[green!60!black, thick] ({tx(x_a)},{ty(y_a)}) -- "
                rf"({tx(x_b)},{ty(y_b)});"
            )
            if label:
                lines.append(
                    rf"  \node[right] at ({tx(x_b)},{ty(y_b)}) "
                    rf"{{{_latex_escape(label)}}};"
                )

        # Secants.
        for x1, x2, label in self._secants:
            y1 = self._f_at(x1)
            y2 = self._f_at(x2)
            if y1 is None or y2 is None:
                continue
            lines.append(
                rf"  \draw[purple, dashed] ({tx(x1)},{ty(y1)}) -- "
                rf"({tx(x2)},{ty(y2)});"
            )
            if label:
                mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                lines.append(
                    rf"  \node[above] at ({tx(mx)},{ty(my)}) "
                    rf"{{{_latex_escape(label)}}};"
                )

        # Critical points.
        for x, label in self._criticals:
            y = self._f_at(x)
            if y is None:
                y = 0.0
            lines.append(
                rf"  \draw[red, dashed] ({tx(x)},{ty(0.0)}) -- "
                rf"({tx(x)},{ty(y)});"
            )
            lines.append(
                rf"  \fill[red] ({tx(x)},{ty(y)}) circle (2pt);"
            )
            if label:
                lines.append(
                    rf"  \node[above right] at ({tx(x)},{ty(y)}) "
                    rf"{{{_latex_escape(label)}}};"
                )

        # Intercepts.
        for axis, value, label in self._intercepts:
            if axis == "x":
                lines.append(
                    rf"  \fill[blue] ({tx(value)},{ty(0.0)}) circle (2pt);"
                )
                pos = (value, 0.0)
            else:
                lines.append(
                    rf"  \fill[blue] ({tx(0.0)},{ty(value)}) circle (2pt);"
                )
                pos = (0.0, value)
            if label:
                lines.append(
                    rf"  \node[above right] at ({tx(pos[0])},{ty(pos[1])}) "
                    rf"{{{_latex_escape(label)}}};"
                )

        lines.append(r"\end{tikzpicture}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # render() — keeps the visual-sandbox `Visual = ...` contract.
    # ------------------------------------------------------------------

    def render(self) -> str:  # type: ignore[override]
        return self.to_svg()


# ---------------------------------------------------------------------------
# Companion: AxesAnnotation — bundle of intercepts / asymptotes / criticals
# ---------------------------------------------------------------------------


@dataclass
class AxesAnnotation:
    """Bundle of axis annotations applied in one go.

    Templates that prepare the annotation set in Python often have all
    three lists (intercepts, asymptotes, critical points) ready at
    once.  Bundling them into a single object keeps the call site
    declarative — ``fig.add_axes_annotation(ann)`` — rather than a
    sprawl of six ``mark_*`` calls.
    """

    intercepts: List[Tuple[str, float]] = field(default_factory=list)
    """List of ``(axis, value)`` pairs. ``axis`` is ``"x"`` or ``"y"``."""

    asymptotes: List[Tuple[str, float]] = field(default_factory=list)
    """List of ``(kind, value)`` pairs. ``kind`` is ``"horizontal"`` or ``"vertical"``."""

    critical_points: List[Tuple[float, str]] = field(default_factory=list)
    """List of ``(x, label)`` pairs. Empty label welcome — pass ``""``."""

    def apply(self, fig: "FunctionGraphFigure") -> None:
        """Apply every queued annotation to ``fig`` in canonical order."""
        for axis, value in self.intercepts:
            fig.mark_intercept(axis, value)
        for kind, value in self.asymptotes:
            fig.mark_asymptote(value, kind=kind)
        for x, label in self.critical_points:
            fig.mark_critical(x, label=label or None)


