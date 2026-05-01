"""γ.4s — :class:`BalanceScale`: two-pan balance for K1 measurement.weight.

A pictorial balance scale with a vertical post, triangular base, beam,
and two suspended pans holding countable items. Each pan's contents
are rendered via :func:`shape_glyph.glyph_for` so the prose-item
vocabulary the K1 corpus already speaks (apples, blocks, books, …)
maps cleanly onto the same six geometric primitives every other K1
visual uses.

The beam tilts when ``show_balance=True`` and the pan counts differ:
the heavier side rotates *down*. Tilt math runs in math-convention
angles internally, then converts to SVG-space (y-down) by negating
the sin term — the same trick :class:`SectorFigure` uses. With
``show_balance=False`` the beam stays level regardless of counts;
templates that want a "set up the equation, don't reveal which side
is heavier" framing pick that mode.

Multi-format rendering follows the γ.3 keystone contract:

- :meth:`to_svg`  — self-contained SVG (also returned by :meth:`render`).
- :meth:`to_text` — one-paragraph ASCII description naming the heavier side.
- :meth:`to_latex` — TikZ ``\\begin{tikzpicture} ... \\end{tikzpicture}``
  using ``[rotate around={...:(...)}]`` scopes for the tilt.

Determinism: same constructor args → byte-identical SVG. All
coordinates route through :func:`_fmt`.
"""

from __future__ import annotations

import math
from typing import List, Tuple

from ..base import DEFAULT_FONT, SVGBuilder, _esc, _fmt, _latex_escape
from .shape_glyph import glyph_for


class BalanceScale(SVGBuilder):
    """Two-pan balance scale with item glyphs and optional tilt.

    Parameters
    ----------
    left_count, right_count:
        Non-negative integers giving the number of items in each pan.
        Negative values raise :class:`ValueError`.
    item:
        Prose-item name (e.g. ``"blocks"``, ``"apples"``); routed
        through :func:`glyph_for` to pick the rendering primitive.
        Unknown items fall back to a circle glyph.
    show_balance:
        When ``True`` (default), the beam tilts toward the heavier
        side if counts differ; equal counts render level. When
        ``False`` the beam stays level regardless — useful for
        "compare these two amounts" framings that don't want to
        give the answer away.
    glyph_size:
        Bounding-box size for each item glyph (SVG units). For very
        crowded pans (``left + right > 20``, a K1 anti-pattern but
        we render anyway) the size is internally scaled down so the
        glyphs still fit the pan.
    glyph_fill:
        Fill colour for the glyphs.
    width, height:
        SVG viewport dimensions.
    """

    # Palette / stroke — kept as class attributes so subclasses or
    # later "darkmode" theming can override without touching render.
    _POST_STROKE = "#444"
    _BEAM_STROKE = "#222"
    _PAN_FILL = "#cbd5e1"
    _PAN_STROKE = "#475569"
    _STRING_STROKE = "#666"
    _STROKE_WIDTH = 2.0
    _PAN_STROKE_WIDTH = 1.5

    # Maximum tilt angle in degrees — applied when counts differ.
    # 15° gives a clearly readable lean without sending pans off-canvas.
    _TILT_DEG = 15.0

    # Length of strings that suspend the pans below the beam.
    _STRING_LEN = 28.0

    # Pan height (the dish's vertical extent), and ratio of beam
    # length to viewport width.
    _PAN_HEIGHT = 8.0
    _BEAM_FRACTION = 0.7

    def __init__(
        self,
        left_count: int,
        right_count: int,
        item: str = "blocks",
        show_balance: bool = True,
        glyph_size: float = 18,
        glyph_fill: str = "#60a5fa",
        width: int = 400,
        height: int = 280,
    ):
        super().__init__(width=width, height=height)
        if int(left_count) < 0:
            raise ValueError(f"left_count must be >= 0, got {left_count}")
        if int(right_count) < 0:
            raise ValueError(f"right_count must be >= 0, got {right_count}")

        self.left_count = int(left_count)
        self.right_count = int(right_count)
        self.item = str(item)
        self.show_balance = bool(show_balance)
        self.glyph_fill = str(glyph_fill)

        # K1 anti-pattern: very many items. We render anyway but
        # squeeze the glyph_size so a 12-deep pyramid still fits the
        # pan width. Threshold mirrors the docstring contract.
        total = self.left_count + self.right_count
        if total > 20:
            scale = max(0.55, 20.0 / total)
            self.glyph_size = float(glyph_size) * scale
        else:
            self.glyph_size = float(glyph_size)

    # ------------------------------------------------------------------
    # Geometry helpers
    # ------------------------------------------------------------------

    def _pivot(self) -> Tuple[float, float]:
        """SVG-space coordinates of the beam pivot (top of the post)."""
        return (self.width / 2.0, self.height * 0.5)

    def _base_y(self) -> float:
        """SVG-space y of the bottom of the post / base centre."""
        return self.height * 0.85

    def _beam_half_length(self) -> float:
        return self.width * self._BEAM_FRACTION / 2.0

    def _tilt_deg(self) -> float:
        """Beam tilt in *SVG-space* degrees (positive = clockwise).

        Positive tilt rotates the right end downward — i.e. the right
        pan ends up lower. We map the count comparison onto this:

        - ``left > right`` (left pan heavier, left should fall) → CCW → negative.
        - ``left < right`` (right pan heavier, right should fall) → CW → positive.
        - equal counts, or ``show_balance=False`` → 0.
        """
        if not self.show_balance:
            return 0.0
        if self.left_count > self.right_count:
            return -self._TILT_DEG
        if self.left_count < self.right_count:
            return self._TILT_DEG
        return 0.0

    def _rotate_around_pivot(
        self, x: float, y: float, deg: float
    ) -> Tuple[float, float]:
        """Rotate ``(x, y)`` around the beam pivot by ``deg`` degrees in SVG-space.

        SVG y-axis points down, so a positive degree value here is a
        *clockwise* rotation as the user sees it on screen. The
        canonical SVG rotation matrix matches that convention without
        any sin-flip — we use it directly.
        """
        cx, cy = self._pivot()
        rad = math.radians(deg)
        dx, dy = x - cx, y - cy
        rx = cx + dx * math.cos(rad) - dy * math.sin(rad)
        ry = cy + dx * math.sin(rad) + dy * math.cos(rad)
        return (rx, ry)

    def _beam_endpoints(self) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """Return ``(left_end, right_end)`` of the beam after tilt."""
        cx, cy = self._pivot()
        L = self._beam_half_length()
        deg = self._tilt_deg()
        left_end = self._rotate_around_pivot(cx - L, cy, deg)
        right_end = self._rotate_around_pivot(cx + L, cy, deg)
        return left_end, right_end

    def _pan_centre(self, beam_end: Tuple[float, float]) -> Tuple[float, float]:
        """Centre of a pan suspended below ``beam_end`` by a vertical string.

        Strings hang straight down regardless of beam tilt — the same
        idealisation a real balance scale uses (the pan's mass keeps
        the string vertical). This also keeps the pan's contents
        readable: glyphs always stack along the SVG y-axis.
        """
        bx, by = beam_end
        return (bx, by + self._STRING_LEN)

    # ------------------------------------------------------------------
    # Item-stacking strategy
    # ------------------------------------------------------------------

    def _stack_positions(
        self, count: int, pan_centre: Tuple[float, float]
    ) -> List[Tuple[float, float]]:
        """Compute (cx, cy) for each item glyph in a pan.

        Strategy:

        - 0: no positions.
        - 1-6: pyramid stack — bottom row first, narrower rows above,
          apex on top. Reads naturally for K1 ("piled up like blocks").
        - 7+: rectangular grid (max 4-wide, then add rows upward).
        """
        if count <= 0:
            return []
        cx, cy_pan = pan_centre
        size = self.glyph_size
        # Items sit *on top of* the pan dish; the bottom of the bottom
        # row lines up with the dish's top edge.
        bottom_y = cy_pan - self._PAN_HEIGHT / 2 - size / 2

        if count <= 6:
            return self._pyramid_positions(count, cx, bottom_y, size)
        return self._grid_positions(count, cx, bottom_y, size)

    def _pyramid_positions(
        self, count: int, cx: float, bottom_y: float, size: float
    ) -> List[Tuple[float, float]]:
        """Pyramid layout for small counts (≤ 6).

        Row sizes are picked so the figure reads as a stable stack:

        ===== =====
        count rows
        ===== =====
        1     [1]
        2     [2]
        3     [3]
        4     [3, 1]
        5     [3, 2]
        6     [3, 2, 1]
        ===== =====
        """
        layouts = {
            1: [1],
            2: [2],
            3: [3],
            4: [3, 1],
            5: [3, 2],
            6: [3, 2, 1],
        }
        rows = layouts[count]
        positions: List[Tuple[float, float]] = []
        # Tighten spacing slightly so 3-wide bottom rows never overflow
        # a default-width pan.
        spacing = size * 1.05
        for row_idx, row_count in enumerate(rows):
            y = bottom_y - row_idx * size * 0.92
            # Centre the row on the pan's centreline.
            row_width = (row_count - 1) * spacing
            x0 = cx - row_width / 2
            for i in range(row_count):
                positions.append((x0 + i * spacing, y))
        return positions

    def _grid_positions(
        self, count: int, cx: float, bottom_y: float, size: float
    ) -> List[Tuple[float, float]]:
        """Compact rectangular grid for high counts (> 6).

        Cap row width at 4 columns; subsequent rows stack upward.
        Rows are filled bottom-up so the visual weight sits on the pan.
        """
        cols = min(4, count)
        spacing = size * 1.0
        positions: List[Tuple[float, float]] = []
        remaining = count
        row_idx = 0
        while remaining > 0:
            row_count = min(cols, remaining)
            y = bottom_y - row_idx * size * 0.95
            row_width = (row_count - 1) * spacing
            x0 = cx - row_width / 2
            for i in range(row_count):
                positions.append((x0 + i * spacing, y))
            remaining -= row_count
            row_idx += 1
        return positions

    # ------------------------------------------------------------------
    # to_svg
    # ------------------------------------------------------------------

    def _pan_svg(self, pan_centre: Tuple[float, float]) -> str:
        """Render a single pan dish (rounded rectangle / shallow ellipse).

        We use a rounded rect rather than a true bowl because (a) it
        composes better with the grid/pyramid stack drawn directly on
        top, and (b) it matches the "tray" iconography K1 worksheets
        already use for balance scales.
        """
        cx, cy = pan_centre
        # Pan width should hold up to ~4 glyphs at full size.
        pan_w = max(self.glyph_size * 4.4, 70.0)
        x = cx - pan_w / 2
        y = cy - self._PAN_HEIGHT / 2
        return (
            f'<rect x="{_fmt(x)}" y="{_fmt(y)}" '
            f'width="{_fmt(pan_w)}" height="{_fmt(self._PAN_HEIGHT)}" '
            f'rx="{_fmt(self._PAN_HEIGHT / 2)}" '
            f'fill="{self._PAN_FILL}" stroke="{self._PAN_STROKE}" '
            f'stroke-width="{_fmt(self._PAN_STROKE_WIDTH)}"/>'
        )

    def to_svg(self) -> str:
        parts: List[str] = []

        cx, cy = self._pivot()
        base_y = self._base_y()

        # ---- Vertical post --------------------------------------------------
        parts.append(
            f'<line x1="{_fmt(cx)}" y1="{_fmt(base_y)}" '
            f'x2="{_fmt(cx)}" y2="{_fmt(cy)}" '
            f'stroke="{self._POST_STROKE}" '
            f'stroke-width="{_fmt(self._STROKE_WIDTH + 1)}" '
            f'stroke-linecap="round"/>'
        )

        # ---- Triangular base ------------------------------------------------
        # Equilateral-ish triangle wider than tall so it reads as
        # "ground-anchored" rather than "spike". The post connects at
        # the apex.
        base_half_w = 30.0
        base_h = 14.0
        tri_points = (
            f"{_fmt(cx)},{_fmt(base_y)} "
            f"{_fmt(cx - base_half_w)},{_fmt(base_y + base_h)} "
            f"{_fmt(cx + base_half_w)},{_fmt(base_y + base_h)}"
        )
        parts.append(
            f'<polygon points="{tri_points}" '
            f'fill="{self._POST_STROKE}" stroke="{self._POST_STROKE}" '
            f'stroke-width="{_fmt(self._STROKE_WIDTH)}" '
            f'stroke-linejoin="round"/>'
        )

        # ---- Beam (tilted) --------------------------------------------------
        left_end, right_end = self._beam_endpoints()
        parts.append(
            f'<line x1="{_fmt(left_end[0])}" y1="{_fmt(left_end[1])}" '
            f'x2="{_fmt(right_end[0])}" y2="{_fmt(right_end[1])}" '
            f'stroke="{self._BEAM_STROKE}" '
            f'stroke-width="{_fmt(self._STROKE_WIDTH + 0.5)}" '
            f'stroke-linecap="round"/>'
        )

        # Pivot dot — small visual anchor at the rotation point.
        parts.append(
            f'<circle cx="{_fmt(cx)}" cy="{_fmt(cy)}" r="3" '
            f'fill="{self._POST_STROKE}"/>'
        )

        # ---- Suspending strings + pans -------------------------------------
        for beam_end in (left_end, right_end):
            pan_centre = self._pan_centre(beam_end)
            # String hangs straight down from the beam end.
            parts.append(
                f'<line x1="{_fmt(beam_end[0])}" y1="{_fmt(beam_end[1])}" '
                f'x2="{_fmt(pan_centre[0])}" y2="{_fmt(pan_centre[1])}" '
                f'stroke="{self._STRING_STROKE}" '
                f'stroke-width="1" stroke-linecap="round"/>'
            )
            parts.append(self._pan_svg(pan_centre))

        # ---- Item glyphs ----------------------------------------------------
        glyph_fn = glyph_for(self.item)
        left_pan_centre = self._pan_centre(left_end)
        right_pan_centre = self._pan_centre(right_end)
        for x, y in self._stack_positions(self.left_count, left_pan_centre):
            parts.append(glyph_fn(x, y, self.glyph_size, self.glyph_fill))
        for x, y in self._stack_positions(self.right_count, right_pan_centre):
            parts.append(glyph_fn(x, y, self.glyph_size, self.glyph_fill))

        return self._wrap(*parts)

    # ------------------------------------------------------------------
    # to_text
    # ------------------------------------------------------------------

    def to_text(self) -> str:
        """One-paragraph ASCII description.

        Names both pan counts, the item, and the comparison outcome
        (heavier side, or balanced) so screen-reader / ASCII-only
        downstream consumers get the same information the SVG conveys.
        """
        item = self.item
        if self.left_count == self.right_count:
            if self.left_count == 1:
                return (
                    f"Balance scale: {self.left_count} {item} on each pan, "
                    f"balanced."
                )
            return (
                f"Balance scale: {self.left_count} {item} on each pan, "
                f"balanced."
            )
        # Unequal counts.
        if self.show_balance:
            if self.left_count > self.right_count:
                outcome = "Left side heavier."
            else:
                outcome = "Right side heavier."
        else:
            outcome = "Balanced (display only)."
        return (
            f"Balance scale: {self.left_count} {item} on the left pan, "
            f"{self.right_count} {item} on the right pan. {outcome}"
        )

    # ------------------------------------------------------------------
    # to_latex (TikZ)
    # ------------------------------------------------------------------

    def to_latex(self) -> str:
        """TikZ rendering.

        Strategy: draw the post + base in their normal frame, then a
        ``[rotate around={...:(pivot)}]`` scope holds the beam line and
        the two pan blobs. Items in each pan are rendered as small
        circles (a deliberate simplification — TikZ output is mostly
        used for printable assignments where the visual fidelity bar is
        lower than for SVG).

        SVG units → cm conversion: 1 cm ≈ 50 SVG units, picked so a
        default 400-px-wide builder fits well under 8 cm wide on the
        page.
        """
        unit = 50.0  # SVG px per cm.
        cx, cy_svg = self._pivot()
        base_y_svg = self._base_y()

        # Convert SVG (y-down) coords to TikZ (y-up): tikz_y = -svg_y.
        def t(x: float, y: float) -> Tuple[float, float]:
            return (x / unit, -y / unit)

        pivot_t = t(cx, cy_svg)
        base_t = t(cx, base_y_svg)
        base_left_t = t(cx - 30.0, base_y_svg + 14.0)
        base_right_t = t(cx + 30.0, base_y_svg + 14.0)

        L = self._beam_half_length() / unit
        tilt = self._tilt_deg()
        # SVG positive deg = CW; TikZ positive deg = CCW. Flip sign.
        tikz_tilt = -tilt

        lines: List[str] = []
        lines.append(r"\begin{tikzpicture}")
        # Post (bottom → pivot).
        lines.append(
            rf"  \draw[line width=1.2pt] "
            rf"({_fmt(base_t[0])},{_fmt(base_t[1])}) -- "
            rf"({_fmt(pivot_t[0])},{_fmt(pivot_t[1])});"
        )
        # Triangular base.
        lines.append(
            rf"  \draw[fill=gray!50] "
            rf"({_fmt(base_t[0])},{_fmt(base_t[1])}) -- "
            rf"({_fmt(base_left_t[0])},{_fmt(base_left_t[1])}) -- "
            rf"({_fmt(base_right_t[0])},{_fmt(base_right_t[1])}) -- cycle;"
        )
        # Beam — rotated scope around the pivot.
        lines.append(
            rf"  \begin{{scope}}[rotate around={{{_fmt(tikz_tilt)}:"
            rf"({_fmt(pivot_t[0])},{_fmt(pivot_t[1])})}}]"
        )
        lines.append(
            rf"    \draw[line width=1.5pt] "
            rf"({_fmt(pivot_t[0] - L)},{_fmt(pivot_t[1])}) -- "
            rf"({_fmt(pivot_t[0] + L)},{_fmt(pivot_t[1])});"
        )
        lines.append(r"  \end{scope}")
        # Pivot dot.
        lines.append(
            rf"  \fill ({_fmt(pivot_t[0])},{_fmt(pivot_t[1])}) "
            rf"circle (1.5pt);"
        )
        # Pans + items: rendered using the *post-rotation* beam
        # endpoints so the strings hang from where the user sees them.
        left_end_svg, right_end_svg = self._beam_endpoints()
        for end_svg, count in (
            (left_end_svg, self.left_count),
            (right_end_svg, self.right_count),
        ):
            ex, ey = t(end_svg[0], end_svg[1])
            pan_centre_svg = self._pan_centre(end_svg)
            px, py = t(pan_centre_svg[0], pan_centre_svg[1])
            # String.
            lines.append(
                rf"  \draw[gray] ({_fmt(ex)},{_fmt(ey)}) -- "
                rf"({_fmt(px)},{_fmt(py)});"
            )
            # Pan: small filled rectangle.
            pan_w = max(self.glyph_size * 4.4, 70.0) / unit
            pan_h = self._PAN_HEIGHT / unit
            lines.append(
                rf"  \draw[fill=gray!30, rounded corners=1pt] "
                rf"({_fmt(px - pan_w / 2)},{_fmt(py - pan_h / 2)}) "
                rf"rectangle "
                rf"({_fmt(px + pan_w / 2)},{_fmt(py + pan_h / 2)});"
            )
            # Items — small circles in pyramid/grid layout.
            r_cm = (self.glyph_size / 2) / unit
            for ix, iy in self._stack_positions(count, pan_centre_svg):
                tx, ty = t(ix, iy)
                lines.append(
                    rf"  \fill[blue!50] ({_fmt(tx)},{_fmt(ty)}) "
                    rf"circle ({_fmt(r_cm)});"
                )

        # Item label, escaped for LaTeX.
        item_label = _latex_escape(self.item)
        lines.append(
            rf"  \node[font=\small] at "
            rf"({_fmt(pivot_t[0])},{_fmt(base_t[1] - 0.3)}) "
            rf"{{Items: {item_label}}};"
        )
        lines.append(r"\end{tikzpicture}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # render() — keeps the visual-sandbox `Visual = ...` contract
    # ------------------------------------------------------------------

    def render(self) -> str:
        return self.to_svg()
