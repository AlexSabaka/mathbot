"""Series RLC circuit schematic builder.

Lays out a voltage source, resistor, inductor, and capacitor on a
rectangular series loop — the canonical N16 sub-pattern (b) circuit
for 2nd-order linear ODE word problems.

Component symbols use the IEEE/IEC conventions readers will recognise:

- Voltage source: circle with `+`/`−` polarity marks, label to the left.
- Resistor: 5-segment zigzag interrupting the wire (US convention).
- Inductor: 4 small arcs ("bumps") forming a coil.
- Capacitor: two short parallel plates perpendicular to the wire.

The layout is deterministic — same labels in, same SVG bytes out — so
the existing fixture-drift lint catches any regression.
"""

from __future__ import annotations

from typing import List, Optional

from .base import DEFAULT_FONT, SVGBuilder, _esc, _fmt


class CircuitSVG(SVGBuilder):
    """Build a series-RLC circuit diagram.

    Usage::

        ckt = CircuitSVG(R="R = 2 Ω", L="L = 1 H", C="C = 1 F", V="V = 0 (free)")
        Visual = ckt.render()

    All four labels are author-supplied free-form strings. Pass an
    empty string to suppress a label without removing the symbol.
    """

    # Loop geometry — fixed margins sized for the typical RLC label
    # length ("R = 2 Ohm", "L = 1 H", "C = 1 F", "V = 12 V"). The
    # source label is anchor=end and right-aligns flush with x=LEFT-26,
    # so leaving 130 px on the left absorbs labels up to ~18 chars
    # without clipping the inner viewBox. Subclasses can override
    # before render() if a non-default page size is needed.
    _LEFT = 130
    _RIGHT = 410
    _TOP = 60
    _BOT = 250

    def __init__(
        self,
        width: int = 500,
        height: int = 320,
        R: str = "R",
        L: str = "L",
        C: str = "C",
        V: str = "V",
        source_disconnected: bool = False,
    ):
        super().__init__(width, height)
        self.R_label = R
        self.L_label = L
        self.C_label = C
        self.V_label = V
        # γ.4q (Q.1). When True, the source position renders as an open
        # gap (two short parallel strokes perpendicular to the wire,
        # mirroring the schematic "switch open" idiom) instead of the
        # default closed-circle source with `+`/`−` polarity marks. Used
        # by RLC-discharge templates that disconnect the source at t=0;
        # the prose says "voltage source disconnected" and the schematic
        # must agree visually (rubric item 12 — schematics don't
        # contradict their labels).
        self.source_disconnected = source_disconnected

    # ------------------------------------------------------------------
    # Component drawers — each renders the symbol at a fixed position
    # on the loop and emits the wire stubs that connect it to the
    # corner nodes.
    # ------------------------------------------------------------------

    def _wire(self, x1: float, y1: float, x2: float, y2: float) -> str:
        return (
            f'<line x1="{_fmt(x1)}" y1="{_fmt(y1)}" '
            f'x2="{_fmt(x2)}" y2="{_fmt(y2)}" '
            f'stroke="#222" stroke-width="1.5"/>'
        )

    def _label(self, x: float, y: float, text: str, anchor: str = "middle") -> str:
        if not text:
            return ""
        return (
            f'<text x="{_fmt(x)}" y="{_fmt(y)}" text-anchor="{anchor}" '
            f'{DEFAULT_FONT}>{_esc(text)}</text>'
        )

    def _resistor(self) -> List[str]:
        """Resistor on the top wire, midpoint at ((L+R)/2, TOP)."""
        cx = (self._LEFT + self._RIGHT) / 2
        # Zigzag is 80px wide × 20px tall (±10 from the wire).
        x0, x1 = cx - 40, cx + 40
        # 5 peaks/valleys spread evenly between x0 and x1.
        # Pattern: wire — \-/\-/\-/\-/ — wire.
        pts: List[str] = [f"{_fmt(x0)},{_fmt(self._TOP)}"]
        amp = 10
        n = 8  # number of zigzag segments between x0 and x1
        for i in range(1, n):
            x = x0 + (x1 - x0) * i / n
            y = self._TOP + (-amp if i % 2 == 1 else amp)
            pts.append(f"{_fmt(x)},{_fmt(y)}")
        pts.append(f"{_fmt(x1)},{_fmt(self._TOP)}")
        zig = (
            f'<polyline fill="none" stroke="#222" stroke-width="1.5" '
            f'points="{" ".join(pts)}"/>'
        )
        return [
            self._wire(self._LEFT, self._TOP, x0, self._TOP),
            zig,
            self._wire(x1, self._TOP, self._RIGHT, self._TOP),
            self._label(cx, self._TOP - 18, self.R_label),
        ]

    def _inductor(self) -> List[str]:
        """Inductor on the right wire, midpoint at (RIGHT, (TOP+BOT)/2)."""
        cy = (self._TOP + self._BOT) / 2
        # 4 bumps × 18px each = 72px tall total; center on cy.
        bump_h = 18
        n = 4
        total = n * bump_h
        y0 = cy - total / 2
        # Build the arc path: M to start, then n half-circle arcs
        # bulging right (outside the loop interior).
        path_d = f"M {_fmt(self._RIGHT)} {_fmt(y0)}"
        for i in range(n):
            # Arc rx=ry=bump_h/2, sweep-flag=1 → bulge to the right.
            path_d += f" a {_fmt(bump_h / 2)} {_fmt(bump_h / 2)} 0 0 1 0 {_fmt(bump_h)}"
        coil = (
            f'<path d="{path_d}" fill="none" '
            f'stroke="#222" stroke-width="1.5"/>'
        )
        return [
            self._wire(self._RIGHT, self._TOP, self._RIGHT, y0),
            coil,
            self._wire(self._RIGHT, y0 + total, self._RIGHT, self._BOT),
            self._label(self._RIGHT + 32, cy + 4, self.L_label, anchor="start"),
        ]

    def _capacitor(self) -> List[str]:
        """Capacitor on the bottom wire, midpoint at ((L+R)/2, BOT)."""
        cx = (self._LEFT + self._RIGHT) / 2
        # Two parallel plates 12px apart, each 28px tall (±14 from wire).
        gap = 12
        plate_h = 28
        x_left = cx - gap / 2
        x_right = cx + gap / 2
        y_top = self._BOT - plate_h / 2
        y_bot = self._BOT + plate_h / 2
        return [
            self._wire(self._LEFT, self._BOT, x_left, self._BOT),
            f'<line x1="{_fmt(x_left)}" y1="{_fmt(y_top)}" '
            f'x2="{_fmt(x_left)}" y2="{_fmt(y_bot)}" '
            f'stroke="#222" stroke-width="1.5"/>',
            f'<line x1="{_fmt(x_right)}" y1="{_fmt(y_top)}" '
            f'x2="{_fmt(x_right)}" y2="{_fmt(y_bot)}" '
            f'stroke="#222" stroke-width="1.5"/>',
            self._wire(x_right, self._BOT, self._RIGHT, self._BOT),
            self._label(cx, y_bot + 18, self.C_label),
        ]

    def _source(self) -> List[str]:
        """Voltage source on the left wire, midpoint at (LEFT, (TOP+BOT)/2)."""
        cy = (self._TOP + self._BOT) / 2

        if self.source_disconnected:
            # γ.4q open-gap variant. Two short parallel strokes
            # perpendicular to the wire, separated by a small gap,
            # rendering the "source removed / open circuit" idiom.
            # The wires from TOP / BOT terminate at the edge of the
            # gap; the gap itself spans `gap_h` vertical pixels.
            gap_h = 14            # total vertical span of the open gap
            tick_w = 14           # horizontal length of each terminator stroke
            top_y = cy - gap_h / 2
            bot_y = cy + gap_h / 2
            terminator_top = (
                f'<line x1="{_fmt(self._LEFT - tick_w / 2)}" y1="{_fmt(top_y)}" '
                f'x2="{_fmt(self._LEFT + tick_w / 2)}" y2="{_fmt(top_y)}" '
                f'stroke="#222" stroke-width="1.5"/>'
            )
            terminator_bot = (
                f'<line x1="{_fmt(self._LEFT - tick_w / 2)}" y1="{_fmt(bot_y)}" '
                f'x2="{_fmt(self._LEFT + tick_w / 2)}" y2="{_fmt(bot_y)}" '
                f'stroke="#222" stroke-width="1.5"/>'
            )
            return [
                self._wire(self._LEFT, self._TOP, self._LEFT, top_y),
                terminator_top,
                terminator_bot,
                self._wire(self._LEFT, bot_y, self._LEFT, self._BOT),
                # V_label still renders to the left when supplied — but
                # authors using `source_disconnected=True` typically set
                # `V=""` because the open gap conveys "disconnected"
                # without text. Empty label suppresses cleanly.
                self._label(self._LEFT - 26, cy + 4, self.V_label, anchor="end"),
            ]

        # Default: closed-circle source with `+` / `−` polarity marks.
        r = 18  # circle radius
        circle = (
            f'<circle cx="{_fmt(self._LEFT)}" cy="{_fmt(cy)}" r="{_fmt(r)}" '
            f'fill="white" stroke="#222" stroke-width="1.5"/>'
        )
        plus = (
            f'<text x="{_fmt(self._LEFT)}" y="{_fmt(cy - 4)}" '
            f'text-anchor="middle" {DEFAULT_FONT}>+</text>'
        )
        minus = (
            f'<text x="{_fmt(self._LEFT)}" y="{_fmt(cy + 12)}" '
            f'text-anchor="middle" {DEFAULT_FONT}>−</text>'
        )
        return [
            self._wire(self._LEFT, self._TOP, self._LEFT, cy - r),
            circle,
            plus,
            minus,
            self._wire(self._LEFT, cy + r, self._LEFT, self._BOT),
            # Label sits to the LEFT of the source (anchor=end so the
            # text right-aligns flush with x=LEFT-26).
            self._label(self._LEFT - 26, cy + 4, self.V_label, anchor="end"),
        ]

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------

    def render(self) -> str:
        parts: List[str] = []
        parts.extend(self._resistor())
        parts.extend(self._inductor())
        parts.extend(self._capacitor())
        parts.extend(self._source())
        return self._wrap(*parts)
