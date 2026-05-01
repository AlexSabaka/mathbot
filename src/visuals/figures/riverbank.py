"""γ.3 (A.2) — RiverbankFigure: parallel-banks optimization scenario.

Stewart's classic related-rates / optimization figure. Two parallel
horizontal riverbanks separated by a fixed width; a path goes from
a start point ``P`` on the top bank to an end point ``Q`` on the
bottom bank, optionally through an intermediate "swim point" along
the destination bank parameterised by ``swim_x``. Used by problems
like "minimize travel time when running speed differs from swim
speed" or related-rates problems involving the angle the swimmer
makes with the bank.

Authoring API mirrors the other Phase γ figure builders — multi-format
output (``to_svg`` / ``to_text`` / ``to_latex``) and ``render()``
returning the SVG so the visual sandbox `Visual = builder.render()`
contract still holds.
"""

from __future__ import annotations

from typing import List, Optional

from ..base import DEFAULT_FONT, SVGBuilder, _esc, _fmt, _latex_escape


class RiverbankFigure(SVGBuilder):
    """Parallel-riverbank figure for optimization / related-rates problems.

    Geometry conventions (data-space):

    - Top bank is the starting bank (point ``P``); bottom bank is the
      destination (point ``Q``).
    - Data unit ``downstream`` is mapped horizontally to a fitted span
      of the canvas; the river width ``bank_distance`` is annotated on
      the left edge but the on-screen vertical separation between the
      banks is fixed (~120 px) so the figure reads consistently across
      varying ``bank_distance`` values.
    - When ``swim_x`` is provided, a swim point ``S`` is rendered on
      the bottom bank at the corresponding horizontal offset, plus
      dashed segments ``P → S`` (the river-crossing leg) and ``S → Q``
      (the along-bank leg).
    """

    # Fixed screen-space y-coordinates for the two banks. The river
    # width annotation reads `label_distance` symbolically; the actual
    # ratio is decoupled from the data-unit value so a "3 km" river
    # doesn't render hilariously squat next to an "8 km" downstream.
    _TOP_BANK_Y = 80
    _BOTTOM_BANK_Y = 200

    # Horizontal margins. Start point P sits at x=_LEFT_MARGIN on the
    # top bank; the rightmost x corresponds to ``downstream`` data
    # units mapped onto the span (canvas - left - right margin).
    _LEFT_MARGIN = 60
    _RIGHT_MARGIN = 60

    _RIVER_FILL = "#bfdbfe"
    _BANK_STROKE = "#1e3a5f"
    _POINT_FILL = "#111"
    _PATH_STROKE = "#c0392b"
    _BRACE_STROKE = "#444"

    def __init__(
        self,
        bank_distance: float = 3,
        downstream: float = 8,
        swim_x: Optional[float] = None,
        label_distance: str = "d",
        label_downstream: str = "8 km",
        label_swim: str = "x",
        width: int = 600,
        height: int = 280,
    ):
        super().__init__(width=width, height=height)
        self.bank_distance = float(bank_distance)
        self.downstream = float(downstream)
        self.swim_x = None if swim_x is None else float(swim_x)
        self.label_distance = str(label_distance)
        self.label_downstream = str(label_downstream)
        self.label_swim = str(label_swim)

    # ------------------------------------------------------------------
    # Coordinate helpers
    # ------------------------------------------------------------------

    def _x_for(self, data_x: float) -> float:
        """Map a data-space x (0 .. ``downstream``) to canvas x."""
        span = self.width - self._LEFT_MARGIN - self._RIGHT_MARGIN
        if self.downstream <= 0:
            return float(self._LEFT_MARGIN)
        frac = data_x / self.downstream
        return self._LEFT_MARGIN + frac * span

    # ------------------------------------------------------------------
    # to_svg
    # ------------------------------------------------------------------

    def to_svg(self) -> str:
        parts: List[str] = []

        x_left = self._LEFT_MARGIN
        x_right = self.width - self._RIGHT_MARGIN
        y_top = self._TOP_BANK_Y
        y_bot = self._BOTTOM_BANK_Y

        # River body (light-blue rectangle between the banks).
        parts.append(
            f'<rect x="{_fmt(x_left)}" y="{_fmt(y_top)}" '
            f'width="{_fmt(x_right - x_left)}" '
            f'height="{_fmt(y_bot - y_top)}" '
            f'fill="{self._RIVER_FILL}" stroke="none"/>'
        )

        # Top bank line.
        parts.append(
            f'<line x1="{_fmt(x_left)}" y1="{_fmt(y_top)}" '
            f'x2="{_fmt(x_right)}" y2="{_fmt(y_top)}" '
            f'stroke="{self._BANK_STROKE}" stroke-width="2"/>'
        )
        # Bottom bank line.
        parts.append(
            f'<line x1="{_fmt(x_left)}" y1="{_fmt(y_bot)}" '
            f'x2="{_fmt(x_right)}" y2="{_fmt(y_bot)}" '
            f'stroke="{self._BANK_STROKE}" stroke-width="2"/>'
        )

        # Start P (top-left bank).
        px, py = self._x_for(0), y_top
        # End Q at horizontal offset = downstream.
        qx, qy = self._x_for(self.downstream), y_bot

        # Optional swim path: P -> S -> Q.
        if self.swim_x is not None:
            sx = self._x_for(self.swim_x)
            sy = y_bot
            # Leg 1 (river crossing): P -> S
            parts.append(
                f'<line x1="{_fmt(px)}" y1="{_fmt(py)}" '
                f'x2="{_fmt(sx)}" y2="{_fmt(sy)}" '
                f'stroke="{self._PATH_STROKE}" stroke-width="1.6" '
                f'stroke-dasharray="6 4"/>'
            )
            # Leg 2 (along bank): S -> Q
            parts.append(
                f'<line x1="{_fmt(sx)}" y1="{_fmt(sy)}" '
                f'x2="{_fmt(qx)}" y2="{_fmt(qy)}" '
                f'stroke="{self._PATH_STROKE}" stroke-width="1.6" '
                f'stroke-dasharray="6 4"/>'
            )
            # Swim-point marker S.
            parts.append(
                f'<circle cx="{_fmt(sx)}" cy="{_fmt(sy)}" r="4" '
                f'fill="{self._POINT_FILL}"/>'
            )
            # Label "S" near the marker.
            parts.append(
                f'<text x="{_fmt(sx)}" y="{_fmt(sy + 18)}" '
                f'text-anchor="middle" {DEFAULT_FONT}>S</text>'
            )
            # Horizontal brace + label for swim_x along the bottom bank,
            # spanning P-projected-to-bottom (x=_LEFT_MARGIN) → S.
            self._append_horizontal_brace(
                parts,
                x_from=px,
                x_to=sx,
                y=y_bot + 28,
                label=self.label_swim,
                upward=False,
            )

        # Endpoint markers (drawn after path so circles sit on top).
        parts.append(
            f'<circle cx="{_fmt(px)}" cy="{_fmt(py)}" r="5" '
            f'fill="{self._POINT_FILL}"/>'
        )
        parts.append(
            f'<text x="{_fmt(px - 10)}" y="{_fmt(py - 6)}" '
            f'text-anchor="end" {DEFAULT_FONT}>P</text>'
        )
        parts.append(
            f'<circle cx="{_fmt(qx)}" cy="{_fmt(qy)}" r="5" '
            f'fill="{self._POINT_FILL}"/>'
        )
        parts.append(
            f'<text x="{_fmt(qx + 10)}" y="{_fmt(qy + 14)}" '
            f'text-anchor="start" {DEFAULT_FONT}>Q</text>'
        )

        # River-width annotation: vertical brace + label on the left
        # outside the river, between the two banks.
        self._append_vertical_brace(
            parts,
            x=x_left - 24,
            y_from=y_top,
            y_to=y_bot,
            label=self.label_distance,
        )

        # Downstream-distance annotation: horizontal brace below the
        # bottom bank from P-projection to Q (covers the full span).
        # When swim_x is also rendered we drop this brace lower so the
        # two horizontal labels don't collide.
        downstream_y = y_bot + (56 if self.swim_x is not None else 28)
        self._append_horizontal_brace(
            parts,
            x_from=px,
            x_to=qx,
            y=downstream_y,
            label=self.label_downstream,
            upward=False,
        )

        return self._wrap(*parts)

    # ------------------------------------------------------------------
    # Brace helpers — small bracket + label
    # ------------------------------------------------------------------

    def _append_vertical_brace(
        self,
        parts: List[str],
        *,
        x: float,
        y_from: float,
        y_to: float,
        label: str,
    ) -> None:
        """Vertical I-bar with serif caps + a centred label to its left."""
        cap = 6  # half-width of the serif caps at top/bottom
        parts.append(
            f'<line x1="{_fmt(x)}" y1="{_fmt(y_from)}" '
            f'x2="{_fmt(x)}" y2="{_fmt(y_to)}" '
            f'stroke="{self._BRACE_STROKE}" stroke-width="1"/>'
        )
        parts.append(
            f'<line x1="{_fmt(x - cap)}" y1="{_fmt(y_from)}" '
            f'x2="{_fmt(x + cap)}" y2="{_fmt(y_from)}" '
            f'stroke="{self._BRACE_STROKE}" stroke-width="1"/>'
        )
        parts.append(
            f'<line x1="{_fmt(x - cap)}" y1="{_fmt(y_to)}" '
            f'x2="{_fmt(x + cap)}" y2="{_fmt(y_to)}" '
            f'stroke="{self._BRACE_STROKE}" stroke-width="1"/>'
        )
        ymid = (y_from + y_to) / 2
        parts.append(
            f'<text x="{_fmt(x - 10)}" y="{_fmt(ymid + 4)}" '
            f'text-anchor="end" {DEFAULT_FONT}>{_esc(label)}</text>'
        )

    def _append_horizontal_brace(
        self,
        parts: List[str],
        *,
        x_from: float,
        x_to: float,
        y: float,
        label: str,
        upward: bool = False,
    ) -> None:
        """Horizontal I-bar with serif caps + a centred label below.

        ``upward=True`` draws the caps pointing up (for braces above
        the figure); the default points down for braces below.
        """
        cap = 6
        parts.append(
            f'<line x1="{_fmt(x_from)}" y1="{_fmt(y)}" '
            f'x2="{_fmt(x_to)}" y2="{_fmt(y)}" '
            f'stroke="{self._BRACE_STROKE}" stroke-width="1"/>'
        )
        cap_dy = -cap if upward else cap
        parts.append(
            f'<line x1="{_fmt(x_from)}" y1="{_fmt(y - cap)}" '
            f'x2="{_fmt(x_from)}" y2="{_fmt(y + cap)}" '
            f'stroke="{self._BRACE_STROKE}" stroke-width="1"/>'
        )
        parts.append(
            f'<line x1="{_fmt(x_to)}" y1="{_fmt(y - cap)}" '
            f'x2="{_fmt(x_to)}" y2="{_fmt(y + cap)}" '
            f'stroke="{self._BRACE_STROKE}" stroke-width="1"/>'
        )
        xmid = (x_from + x_to) / 2
        # Label sits just outside the brace in the cap direction.
        label_y = y + (cap_dy * 2) - (4 if upward else -14)
        parts.append(
            f'<text x="{_fmt(xmid)}" y="{_fmt(label_y)}" '
            f'text-anchor="middle" {DEFAULT_FONT}>{_esc(label)}</text>'
        )

    # ------------------------------------------------------------------
    # to_text
    # ------------------------------------------------------------------

    def to_text(self) -> str:
        bank = self._fmt_value(self.bank_distance)
        down = self._fmt_value(self.downstream)
        base = (
            f"Two parallel riverbanks {bank} units apart. "
            f"Start point P on the top bank, end point Q on the "
            f"bottom bank {down} units downstream."
        )
        if self.swim_x is not None:
            sx = self._fmt_value(self.swim_x)
            base += f" A candidate path crosses at x={sx} from P."
        return base

    @staticmethod
    def _fmt_value(v: float) -> str:
        if v == int(v):
            return str(int(v))
        return _fmt(v, 3)

    # ------------------------------------------------------------------
    # to_latex (TikZ)
    # ------------------------------------------------------------------

    def to_latex(self) -> str:
        # Map the same data-space coordinates onto a TikZ canvas in
        # cm. Use a downstream-width of 8 cm + bank-distance of 2 cm
        # so the figure reads in a typical column.
        if self.downstream <= 0:
            bank = self._fmt_value(self.bank_distance)
            down = self._fmt_value(self.downstream)
            return (
                "\\fbox{[Figure: parallel riverbanks, "
                f"width {bank}, downstream {down}]" + "}"
            )

        scale_x = 8.0 / self.downstream
        # TikZ y grows upward; place top bank at y=2, bottom at y=0.
        bottom_y = 0.0
        top_y = 2.0

        def tx(x: float) -> str:
            return _fmt(x * scale_x, 3)

        lines: List[str] = []
        lines.append(r"\begin{tikzpicture}[>=stealth]")
        # River fill rectangle.
        lines.append(
            rf"  \fill[blue!15] (0,{_fmt(bottom_y)}) rectangle "
            rf"({tx(self.downstream)},{_fmt(top_y)});"
        )
        # Banks.
        lines.append(
            rf"  \draw[thick] (0,{_fmt(top_y)}) -- "
            rf"({tx(self.downstream)},{_fmt(top_y)});"
        )
        lines.append(
            rf"  \draw[thick] (0,{_fmt(bottom_y)}) -- "
            rf"({tx(self.downstream)},{_fmt(bottom_y)});"
        )
        # P (start) and Q (end) points.
        lines.append(
            rf"  \filldraw (0,{_fmt(top_y)}) circle (2pt) "
            rf"node[above left] {{$P$}};"
        )
        lines.append(
            rf"  \filldraw ({tx(self.downstream)},{_fmt(bottom_y)}) "
            rf"circle (2pt) node[below right] {{$Q$}};"
        )
        # River-width brace on the left.
        lines.append(
            rf"  \draw[decorate,decoration={{brace,amplitude=4pt}}] "
            rf"(-0.2,{_fmt(top_y)}) -- (-0.2,{_fmt(bottom_y)}) "
            rf"node[midway,left=4pt] {{${_latex_escape(self.label_distance)}$}};"
        )
        # Downstream brace below the bottom bank.
        downstream_brace_y = bottom_y - (0.6 if self.swim_x is not None else 0.3)
        lines.append(
            rf"  \draw[decorate,decoration={{brace,mirror,amplitude=4pt}}] "
            rf"(0,{_fmt(downstream_brace_y)}) -- "
            rf"({tx(self.downstream)},{_fmt(downstream_brace_y)}) "
            rf"node[midway,below=4pt] {{${_latex_escape(self.label_downstream)}$}};"
        )
        # Optional swim point + path.
        if self.swim_x is not None:
            lines.append(
                rf"  \filldraw ({tx(self.swim_x)},{_fmt(bottom_y)}) "
                rf"circle (1.6pt) node[below right] {{$S$}};"
            )
            lines.append(
                rf"  \draw[dashed,red!70!black] (0,{_fmt(top_y)}) -- "
                rf"({tx(self.swim_x)},{_fmt(bottom_y)});"
            )
            lines.append(
                rf"  \draw[dashed,red!70!black] "
                rf"({tx(self.swim_x)},{_fmt(bottom_y)}) -- "
                rf"({tx(self.downstream)},{_fmt(bottom_y)});"
            )
            lines.append(
                rf"  \draw[decorate,decoration={{brace,mirror,amplitude=3pt}}] "
                rf"(0,{_fmt(bottom_y - 0.25)}) -- "
                rf"({tx(self.swim_x)},{_fmt(bottom_y - 0.25)}) "
                rf"node[midway,below=2pt] "
                rf"{{${_latex_escape(self.label_swim)}$}};"
            )
        lines.append(r"\end{tikzpicture}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # render() — keeps `Visual = builder.render()` contract.
    # ------------------------------------------------------------------

    def render(self) -> str:
        return self.to_svg()


