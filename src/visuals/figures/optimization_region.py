"""γ.3 (A.2) — :class:`OptimizationRegionFigure`: feasible region of a 2D LP.

Renders the polygonal intersection of half-planes defined by linear
constraints ``a·x + b·y {≤,=,≥} c`` on a coordinate axis frame, with
optional gradient-of-objective arrow. Targets the linear-programming
visuals shipping under the K11–K12 corpus expansion (Simplex /
geometric-LP problems whose answer is a vertex of the feasible
region).

Multi-format follows the γ.3 keystone contract:

- :meth:`to_svg`  — self-contained SVG (also returned by :meth:`render`).
- :meth:`to_text` — sentence listing constraints + computed vertices.
- :meth:`to_latex` — TikZ ``\\begin{tikzpicture} ... \\end{tikzpicture}``
  with axes, constraint lines, and a filled polygon. Falls back to
  ``\\fbox{[Figure: ...]}`` when there's no feasible region.

Determinism: same constructor args → byte-identical SVG. Vertex
sorting is centroid-CCW with deterministic tie-breaking (atan2 first,
distance from centroid second), and every coordinate routes through
:func:`_fmt`.
"""

from __future__ import annotations

import math
from typing import List, Optional, Tuple

from ..base import DEFAULT_FONT, SVGBuilder, _esc, _fmt, _latex_escape


# (a, b, op, c) — represents a·x + b·y {op} c, where op is 'le', 'ge', 'eq'.
Constraint = Tuple[float, float, str, float]

_VALID_OPS = ("le", "ge", "eq")
_TOL = 1e-9


class OptimizationRegionFigure(SVGBuilder):
    """Feasible region of a 2D linear program.

    Parameters
    ----------
    constraints:
        List of ``(a, b, op, c)`` tuples. ``op`` is one of ``'le'``,
        ``'ge'``, ``'eq'`` and represents ``a·x + b·y {op} c``.
    objective_coeffs:
        Optional ``(cx, cy)``. When set, a small gradient arrow
        ``∇f = (cx, cy)`` is drawn at the centroid of the feasible
        region — visualises the direction the LP objective increases.
    x_range, y_range:
        Optional explicit axis ranges. When ``None`` we auto-fit using
        the union of constraint axis-intercepts padded by 20 %.
    title:
        Optional title above the axis frame.
    width, height:
        SVG viewport dimensions.
    """

    # Visual palette — class attributes so subclasses can re-skin without
    # duplicating render code.
    _REGION_FILL = "#e0e7ff"
    _REGION_STROKE = "#000"
    _LINE_STROKE = "#000"
    _AXIS_STROKE = "#333"
    _GRID_STROKE = "#eee"
    _ARROW_STROKE = "#c33"

    def __init__(
        self,
        constraints: List[Constraint],
        objective_coeffs: Optional[Tuple[float, float]] = None,
        x_range: Optional[Tuple[float, float]] = None,
        y_range: Optional[Tuple[float, float]] = None,
        title: Optional[str] = None,
        width: int = 400,
        height: int = 400,
    ):
        super().__init__(width=width, height=height)

        if not constraints:
            raise ValueError("constraints: at least one constraint required")
        normed: List[Constraint] = []
        for i, c in enumerate(constraints):
            if len(c) != 4:
                raise ValueError(
                    f"constraint {i}: expected (a, b, op, c) tuple, got {c!r}"
                )
            a, b, op, rhs = c
            if op not in _VALID_OPS:
                raise ValueError(
                    f"constraint {i}: op {op!r} not in {_VALID_OPS}"
                )
            if a == 0 and b == 0:
                raise ValueError(
                    f"constraint {i}: a and b cannot both be zero"
                )
            normed.append((float(a), float(b), op, float(rhs)))
        self.constraints: List[Constraint] = normed

        self.objective_coeffs: Optional[Tuple[float, float]] = (
            (float(objective_coeffs[0]), float(objective_coeffs[1]))
            if objective_coeffs is not None
            else None
        )
        self.title = title
        self._x_range_explicit = x_range
        self._y_range_explicit = y_range

        # Plot frame margins (mirrors PlotSVG conventions). Wider left
        # margin reserves space for y-axis tick labels.
        self._margin_l = 40
        self._margin_r = 16
        self._margin_t = 28 if title else 16
        self._margin_b = 28

        x_lo, x_hi, y_lo, y_hi = self._compute_ranges()
        self.x_min, self.x_max = x_lo, x_hi
        self.y_min, self.y_max = y_lo, y_hi

        # Compute feasible-region vertices once at construction so
        # to_text / to_svg / to_latex agree on geometry.
        self._vertices: List[Tuple[float, float]] = self._compute_vertices()

    # ------------------------------------------------------------------
    # Range auto-fit
    # ------------------------------------------------------------------

    def _compute_ranges(self) -> Tuple[float, float, float, float]:
        """Auto-fit ``x_range`` / ``y_range`` from constraint axis-intercepts.

        For each constraint ``a·x + b·y = c`` we collect the x-intercept
        (``c/a`` when ``a ≠ 0``) and y-intercept (``c/b`` when ``b ≠ 0``).
        Origin is included so 0 is always inside the frame for typical
        LPs (``x ≥ 0, y ≥ 0`` plus a couple of capacity constraints).
        Range is padded by 20 % on each side; degenerate ranges (e.g.
        all intercepts collapse to a single value) get a fallback span
        of ``[-1, 10]``.
        """
        x_intercepts = [0.0]
        y_intercepts = [0.0]
        for a, b, _op, c in self.constraints:
            if abs(a) > _TOL:
                x_intercepts.append(c / a)
            if abs(b) > _TOL:
                y_intercepts.append(c / b)

        x_lo, x_hi = min(x_intercepts), max(x_intercepts)
        y_lo, y_hi = min(y_intercepts), max(y_intercepts)

        if self._x_range_explicit is not None:
            x_lo, x_hi = (
                float(self._x_range_explicit[0]),
                float(self._x_range_explicit[1]),
            )
        else:
            if x_hi - x_lo < _TOL:
                x_lo, x_hi = -1.0, 10.0
            else:
                pad = (x_hi - x_lo) * 0.2
                x_lo -= pad
                x_hi += pad

        if self._y_range_explicit is not None:
            y_lo, y_hi = (
                float(self._y_range_explicit[0]),
                float(self._y_range_explicit[1]),
            )
        else:
            if y_hi - y_lo < _TOL:
                y_lo, y_hi = -1.0, 10.0
            else:
                pad = (y_hi - y_lo) * 0.2
                y_lo -= pad
                y_hi += pad

        return x_lo, x_hi, y_lo, y_hi

    # ------------------------------------------------------------------
    # Half-plane intersection geometry
    # ------------------------------------------------------------------

    @staticmethod
    def _line_intersect(
        a1: float, b1: float, c1: float,
        a2: float, b2: float, c2: float,
    ) -> Optional[Tuple[float, float]]:
        """Solve the 2×2 linear system ``a1·x + b1·y = c1, a2·x + b2·y = c2``.

        Returns ``None`` when the lines are parallel (det ≈ 0).
        """
        det = a1 * b2 - a2 * b1
        if abs(det) < _TOL:
            return None
        x = (c1 * b2 - c2 * b1) / det
        y = (a1 * c2 - a2 * c1) / det
        return (x, y)

    def _satisfies(self, x: float, y: float) -> bool:
        """Check that ``(x, y)`` satisfies every constraint within tolerance."""
        for a, b, op, c in self.constraints:
            v = a * x + b * y
            if op == "le":
                if v > c + _TOL:
                    return False
            elif op == "ge":
                if v < c - _TOL:
                    return False
            else:  # eq
                if abs(v - c) > _TOL:
                    return False
        return True

    def _compute_vertices(self) -> List[Tuple[float, float]]:
        """Return the feasible-region vertices in counter-clockwise order.

        Algorithm:

        1. For each pair of constraint lines, compute the intersection.
        2. Also intersect each constraint line with the four axis-range
           edges so unbounded regions clip cleanly to the visible frame.
        3. Keep intersections that satisfy *every* constraint (within
           ``_TOL``) AND lie inside the axis-range box (with the same
           tolerance on the box too).
        4. Deduplicate close-by points (same tolerance).
        5. Sort counter-clockwise around the centroid.

        Returns an empty list when the feasible region is empty —
        callers downstream render an empty polygon and the to_text /
        alt-text describe the empty region.
        """
        # Treat the axis-range edges as additional "boundary lines" so
        # unbounded regions get clipped to the visible frame.
        line_set: List[Tuple[float, float, float]] = [
            (a, b, c) for a, b, _op, c in self.constraints
        ]
        line_set.append((1.0, 0.0, self.x_min))
        line_set.append((1.0, 0.0, self.x_max))
        line_set.append((0.0, 1.0, self.y_min))
        line_set.append((0.0, 1.0, self.y_max))

        candidates: List[Tuple[float, float]] = []
        for i in range(len(line_set)):
            for j in range(i + 1, len(line_set)):
                a1, b1, c1 = line_set[i]
                a2, b2, c2 = line_set[j]
                pt = self._line_intersect(a1, b1, c1, a2, b2, c2)
                if pt is None:
                    continue
                x, y = pt
                # Reject points outside the axis-range box (with tol).
                if (
                    x < self.x_min - _TOL
                    or x > self.x_max + _TOL
                    or y < self.y_min - _TOL
                    or y > self.y_max + _TOL
                ):
                    continue
                if not self._satisfies(x, y):
                    continue
                candidates.append((x, y))

        # Dedup near-coincident points.
        unique: List[Tuple[float, float]] = []
        for x, y in candidates:
            if not any(
                abs(x - ux) < 1e-7 and abs(y - uy) < 1e-7 for ux, uy in unique
            ):
                unique.append((x, y))

        if len(unique) < 2:
            # Fewer than 2 vertices means the region is either empty or
            # a single point — neither is renderable as a polygon.
            return unique

        # CCW sort around centroid. Distance secondary key keeps the
        # ordering deterministic when several vertices share an angle
        # (degenerate rectangle corners pinned to the axis range).
        cx = sum(p[0] for p in unique) / len(unique)
        cy = sum(p[1] for p in unique) / len(unique)
        unique.sort(
            key=lambda p: (math.atan2(p[1] - cy, p[0] - cx),
                           (p[0] - cx) ** 2 + (p[1] - cy) ** 2)
        )
        return unique

    # ------------------------------------------------------------------
    # Coordinate transform
    # ------------------------------------------------------------------

    def _data_to_px(self, x: float, y: float) -> Tuple[float, float]:
        plot_w = self.width - self._margin_l - self._margin_r
        plot_h = self.height - self._margin_t - self._margin_b
        sx = self._margin_l + (x - self.x_min) / (self.x_max - self.x_min) * plot_w
        # SVG y points down, math y points up — flip.
        sy = self._margin_t + (self.y_max - y) / (self.y_max - self.y_min) * plot_h
        return sx, sy

    def _line_clip_to_frame(
        self, a: float, b: float, c: float
    ) -> Optional[Tuple[Tuple[float, float], Tuple[float, float]]]:
        """Return the two endpoints where line ``a·x + b·y = c`` exits the axis frame.

        Used to draw constraint boundary lines across the visible plot
        without overshooting. Returns ``None`` if the line misses the
        frame entirely.
        """
        pts: List[Tuple[float, float]] = []
        # Intersect with x = x_min and x = x_max.
        if abs(b) > _TOL:
            for x_edge in (self.x_min, self.x_max):
                y = (c - a * x_edge) / b
                if self.y_min - _TOL <= y <= self.y_max + _TOL:
                    pts.append((x_edge, y))
        # Intersect with y = y_min and y = y_max.
        if abs(a) > _TOL:
            for y_edge in (self.y_min, self.y_max):
                x = (c - b * y_edge) / a
                if self.x_min - _TOL <= x <= self.x_max + _TOL:
                    pts.append((x, y_edge))
        # Dedupe near-equals.
        uniq: List[Tuple[float, float]] = []
        for x, y in pts:
            if not any(abs(x - ux) < 1e-7 and abs(y - uy) < 1e-7 for ux, uy in uniq):
                uniq.append((x, y))
        if len(uniq) < 2:
            return None
        # Pick the two extreme points (largest separation) — handles
        # corner-on-corner intersections cleanly.
        uniq.sort()
        return uniq[0], uniq[-1]

    # ------------------------------------------------------------------
    # to_svg
    # ------------------------------------------------------------------

    def to_svg(self) -> str:
        parts: List[str] = []
        plot_w = self.width - self._margin_l - self._margin_r
        plot_h = self.height - self._margin_t - self._margin_b

        # Frame.
        parts.append(
            f'<rect x="{self._margin_l}" y="{self._margin_t}" '
            f'width="{plot_w}" height="{plot_h}" fill="white" '
            f'stroke="{self._AXIS_STROKE}" stroke-width="1"/>'
        )

        # Title.
        if self.title:
            parts.append(
                f'<text x="{self.width / 2}" y="18" text-anchor="middle" '
                f'{DEFAULT_FONT}>{_esc(self.title)}</text>'
            )

        # Integer-tick gridlines + tick labels.
        x_ticks = self._integer_ticks(self.x_min, self.x_max)
        y_ticks = self._integer_ticks(self.y_min, self.y_max)
        for tx in x_ticks:
            sx, _ = self._data_to_px(tx, self.y_min)
            parts.append(
                f'<line x1="{_fmt(sx)}" y1="{self._margin_t}" '
                f'x2="{_fmt(sx)}" y2="{self._margin_t + plot_h}" '
                f'stroke="{self._GRID_STROKE}" stroke-width="1"/>'
            )
            parts.append(
                f'<text x="{_fmt(sx)}" y="{self._margin_t + plot_h + 14}" '
                f'text-anchor="middle" {DEFAULT_FONT}>{_fmt(tx)}</text>'
            )
        for ty in y_ticks:
            _, sy = self._data_to_px(self.x_min, ty)
            parts.append(
                f'<line x1="{self._margin_l}" y1="{_fmt(sy)}" '
                f'x2="{self._margin_l + plot_w}" y2="{_fmt(sy)}" '
                f'stroke="{self._GRID_STROKE}" stroke-width="1"/>'
            )
            parts.append(
                f'<text x="{self._margin_l - 4}" y="{_fmt(sy + 4)}" '
                f'text-anchor="end" {DEFAULT_FONT}>{_fmt(ty)}</text>'
            )

        # Zero axes (drawn slightly stronger than gridlines when in range).
        if self.x_min < 0 < self.x_max:
            zx, _ = self._data_to_px(0, self.y_min)
            parts.append(
                f'<line x1="{_fmt(zx)}" y1="{self._margin_t}" '
                f'x2="{_fmt(zx)}" y2="{self._margin_t + plot_h}" '
                f'stroke="#999" stroke-width="1"/>'
            )
        if self.y_min < 0 < self.y_max:
            _, zy = self._data_to_px(self.x_min, 0)
            parts.append(
                f'<line x1="{self._margin_l}" y1="{_fmt(zy)}" '
                f'x2="{self._margin_l + plot_w}" y2="{_fmt(zy)}" '
                f'stroke="#999" stroke-width="1"/>'
            )

        # Feasible-region polygon (drawn first so constraint lines overlay).
        if len(self._vertices) >= 3:
            pts = " ".join(
                f"{_fmt(self._data_to_px(x, y)[0])},{_fmt(self._data_to_px(x, y)[1])}"
                for x, y in self._vertices
            )
            parts.append(
                f'<polygon points="{pts}" fill="{self._REGION_FILL}" '
                f'stroke="{self._REGION_STROKE}" stroke-width="1.2"/>'
            )
        elif len(self._vertices) == 2:
            # Equality-only / line-segment region — draw a thick stroke
            # so the "polygon" is still visible.
            (x1, y1), (x2, y2) = self._vertices
            sx1, sy1 = self._data_to_px(x1, y1)
            sx2, sy2 = self._data_to_px(x2, y2)
            parts.append(
                f'<polygon points="{_fmt(sx1)},{_fmt(sy1)} {_fmt(sx2)},{_fmt(sy2)}" '
                f'fill="none" stroke="{self._REGION_STROKE}" stroke-width="2.4"/>'
            )
        else:
            # Empty feasible region — emit an empty polygon so
            # "polygon element present" assertions still pass.
            parts.append(
                f'<polygon points="" fill="{self._REGION_FILL}" '
                f'stroke="{self._REGION_STROKE}" stroke-width="1.2"/>'
            )

        # Constraint boundary lines.
        for a, b, _op, c in self.constraints:
            seg = self._line_clip_to_frame(a, b, c)
            if seg is None:
                continue
            (x1, y1), (x2, y2) = seg
            sx1, sy1 = self._data_to_px(x1, y1)
            sx2, sy2 = self._data_to_px(x2, y2)
            parts.append(
                f'<line x1="{_fmt(sx1)}" y1="{_fmt(sy1)}" '
                f'x2="{_fmt(sx2)}" y2="{_fmt(sy2)}" '
                f'stroke="{self._LINE_STROKE}" stroke-width="1"/>'
            )

        # Objective gradient arrow.
        if self.objective_coeffs is not None and self._vertices:
            cx_data = sum(p[0] for p in self._vertices) / len(self._vertices)
            cy_data = sum(p[1] for p in self._vertices) / len(self._vertices)
            cx, cy = self._data_to_px(cx_data, cy_data)
            ox, oy = self.objective_coeffs
            mag = math.hypot(ox, oy)
            if mag > _TOL:
                # Normalise + scale to a fixed pixel length so the arrow
                # is legible regardless of objective magnitude.
                arrow_len = 30.0
                ux = ox / mag * arrow_len
                # Flip y for SVG (y-down).
                uy = -oy / mag * arrow_len
                ex = cx + ux
                ey = cy + uy
                parts.append(
                    f'<line x1="{_fmt(cx)}" y1="{_fmt(cy)}" '
                    f'x2="{_fmt(ex)}" y2="{_fmt(ey)}" '
                    f'stroke="{self._ARROW_STROKE}" stroke-width="1.6"/>'
                )
                # Arrowhead — two short strokes back from the tip.
                head_len = 6.0
                ang = math.atan2(uy, ux)
                hx1 = ex - head_len * math.cos(ang - math.pi / 6)
                hy1 = ey - head_len * math.sin(ang - math.pi / 6)
                hx2 = ex - head_len * math.cos(ang + math.pi / 6)
                hy2 = ey - head_len * math.sin(ang + math.pi / 6)
                parts.append(
                    f'<line x1="{_fmt(ex)}" y1="{_fmt(ey)}" '
                    f'x2="{_fmt(hx1)}" y2="{_fmt(hy1)}" '
                    f'stroke="{self._ARROW_STROKE}" stroke-width="1.6"/>'
                )
                parts.append(
                    f'<line x1="{_fmt(ex)}" y1="{_fmt(ey)}" '
                    f'x2="{_fmt(hx2)}" y2="{_fmt(hy2)}" '
                    f'stroke="{self._ARROW_STROKE}" stroke-width="1.6"/>'
                )

        return self._wrap(*parts)

    @staticmethod
    def _integer_ticks(lo: float, hi: float) -> List[int]:
        """Integer tick values inside ``[lo, hi]``.

        For wide ranges we down-sample to ≤ 12 ticks so tick labels
        don't pile on top of each other.
        """
        start = math.ceil(lo)
        end = math.floor(hi)
        if end < start:
            return []
        ticks = list(range(start, end + 1))
        if len(ticks) > 12:
            step = max(1, len(ticks) // 12)
            ticks = ticks[::step]
        return ticks

    # ------------------------------------------------------------------
    # to_text
    # ------------------------------------------------------------------

    def to_text(self) -> str:
        """One-sentence description listing constraints and vertices."""
        constraint_strs = [self._constraint_to_str(c) for c in self.constraints]
        constraints_part = ", ".join(constraint_strs)
        if not self._vertices:
            return (
                f"Feasible region defined by {constraints_part}. "
                f"No feasible region (constraints inconsistent)."
            )
        # Normalise -0.0 → 0 so vertex tuples read cleanly.
        def _norm(v: float) -> float:
            return 0.0 if abs(v) < 1e-7 else v
        verts = ", ".join(
            f"({_fmt(_norm(x))},{_fmt(_norm(y))})" for x, y in self._vertices
        )
        return (
            f"Feasible region defined by {constraints_part}. "
            f"Vertices at {verts}."
        )

    @staticmethod
    def _constraint_to_str(c: Constraint) -> str:
        """Render one constraint as ``"a·x + b·y ≤ c"`` style."""
        a, b, op, rhs = c
        sym = {"le": "≤", "ge": "≥", "eq": "="}[op]
        # Build LHS, suppressing zero-coefficient terms.
        terms: List[str] = []
        if abs(a) > _TOL:
            if abs(a - 1) < _TOL:
                terms.append("x")
            elif abs(a + 1) < _TOL:
                terms.append("-x")
            else:
                terms.append(f"{_fmt(a)}x")
        if abs(b) > _TOL:
            if abs(b - 1) < _TOL:
                terms.append("y" if not terms else "+ y")
            elif abs(b + 1) < _TOL:
                terms.append("-y" if not terms else "- y")
            else:
                if terms and b > 0:
                    terms.append(f"+ {_fmt(b)}y")
                elif terms and b < 0:
                    terms.append(f"- {_fmt(abs(b))}y")
                else:
                    terms.append(f"{_fmt(b)}y")
        lhs = " ".join(terms) if terms else "0"
        return f"{lhs} {sym} {_fmt(rhs)}"

    # ------------------------------------------------------------------
    # to_latex
    # ------------------------------------------------------------------

    def to_latex(self) -> str:
        """TikZ rendering of axes + constraint lines + region polygon.

        Falls back to ``\\fbox{[Figure: ...]}`` only when the feasible
        region is empty — the description is more useful than a blank
        TikZ picture in that case.
        """
        if not self._vertices:
            desc = self.to_text()
            return rf"\fbox{{[Figure: {_latex_escape(desc)}]}}"

        # Scale data coordinates to TikZ cm — pick a scale so the
        # diagram fits ~8 cm wide (a typical column width).
        x_span = self.x_max - self.x_min
        y_span = self.y_max - self.y_min
        scale_x = 8.0 / x_span if x_span > _TOL else 1.0
        scale_y = 8.0 / y_span if y_span > _TOL else 1.0
        # Use the smaller scale for both axes so the picture stays square-ish.
        scale = min(scale_x, scale_y)

        def tx(x: float, y: float) -> Tuple[str, str]:
            return _fmt((x - self.x_min) * scale), _fmt((y - self.y_min) * scale)

        lines: List[str] = []
        lines.append(r"\begin{tikzpicture}")

        # Axes box.
        x0, y0 = tx(self.x_min, self.y_min)
        x1, y1 = tx(self.x_max, self.y_max)
        lines.append(rf"  \draw[->] ({x0},{y0}) -- ({x1},{y0});")
        lines.append(rf"  \draw[->] ({x0},{y0}) -- ({x0},{y1});")

        # Region polygon.
        poly_pts = " -- ".join(
            f"({tx(x, y)[0]},{tx(x, y)[1]})" for x, y in self._vertices
        )
        if len(self._vertices) >= 3:
            lines.append(rf"  \draw[fill=blue!10] {poly_pts} -- cycle;")
        else:
            lines.append(rf"  \draw[thick] {poly_pts};")

        # Constraint lines, clipped to the frame.
        for a, b, _op, c in self.constraints:
            seg = self._line_clip_to_frame(a, b, c)
            if seg is None:
                continue
            (lx1, ly1), (lx2, ly2) = seg
            sx1, sy1 = tx(lx1, ly1)
            sx2, sy2 = tx(lx2, ly2)
            lines.append(rf"  \draw[thin] ({sx1},{sy1}) -- ({sx2},{sy2});")

        if self.objective_coeffs is not None:
            cx_data = sum(p[0] for p in self._vertices) / len(self._vertices)
            cy_data = sum(p[1] for p in self._vertices) / len(self._vertices)
            ox, oy = self.objective_coeffs
            mag = math.hypot(ox, oy)
            if mag > _TOL:
                # 1 cm arrow (roughly) regardless of objective magnitude.
                ex_data = cx_data + ox / mag * (1.0 / scale)
                ey_data = cy_data + oy / mag * (1.0 / scale)
                cx, cy = tx(cx_data, cy_data)
                ex, ey = tx(ex_data, ey_data)
                lines.append(rf"  \draw[->,red] ({cx},{cy}) -- ({ex},{ey});")

        lines.append(r"\end{tikzpicture}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # render() default — keeps the visual-sandbox `Visual = ...` contract
    # ------------------------------------------------------------------

    def render(self) -> str:
        return self.to_svg()
