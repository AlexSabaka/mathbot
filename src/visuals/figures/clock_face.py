"""γ.4s — :class:`ClockFace`: analog clock face for K1 measurement.time.

Renders a round, two-handed analog clock with hour numerals 1-12,
twelve hour tick marks, and (optionally) sixty minute tick marks.
The K1 corpus uses this primitive to support time-reading templates
("What time does this clock show?") and time-arithmetic templates
("If the time is 3:00 now, what time was it 30 minutes ago?").

Multi-format rendering follows the γ.3 keystone contract every figure
builder shares:

- :meth:`to_svg` — self-contained SVG (also returned by :meth:`render`).
- :meth:`to_text` — one-paragraph ASCII description in ``Clock showing
  H:MM.`` form so screen-reader / dataset-text fallbacks have a clean
  human-readable string.
- :meth:`to_latex` — TikZ ``\\begin{tikzpicture} ... \\end{tikzpicture}``;
  a clock face is well-suited to TikZ (one ``\\draw circle``, twelve
  ``\\node`` numerals, two ``\\draw`` lines for the hands).

Angle convention
----------------
The arithmetic is done in *clock-face* convention: 0° points straight
up (the 12), angles increase *clockwise* — i.e. 90° is the 3, 180° is
the 6, 270° is the 9. To convert to the math convention used by the
shared ``_polar``-style trig helpers (CCW from +x axis, y-up), every
clock-face angle ``θ_clock`` is rewritten as

    θ_math = 90° − θ_clock

so the 12 (clock 0°) maps to math 90° (straight up), the 3 (clock 90°)
maps to math 0° (positive-x), and so on. SVG itself is y-down, so the
final pixel coordinate uses ``cy − r·sin(θ_math)`` to flip vertically.
This is the same trick :class:`SectorFigure._polar` uses, just with the
extra clock→math rotation baked in.

Determinism: same constructor args → byte-identical SVG. All
geometry resolves to floats formatted through :func:`_fmt`, which
strips trailing zeros so renderers don't shift coordinate strings
underneath us.
"""

from __future__ import annotations

import math
from typing import List, Tuple

from ..base import DEFAULT_FONT, SVGBuilder, _esc, _fmt, _latex_escape


class ClockFace(SVGBuilder):
    """Analog clock face with hour and minute hands.

    Parameters
    ----------
    hour:
        Hour value 1-12. ``0`` is treated as 12 (midnight/noon
        convention). Values >12 reduce mod 12 (so ``hour=13`` shows 1).
    minute:
        Minute value 0-59. ``60`` rolls over to the next hour.
    radius:
        Face radius in SVG units.
    show_minute_marks:
        When ``True`` (default) draws sixty thin tick marks at every
        minute. When ``False`` only the twelve hour ticks are drawn —
        useful for very-young learners where minute granularity is
        a distraction.
    width, height:
        SVG viewport dimensions. The face centres in the viewport.
    """

    # Stroke / fill palette — exposed as class attributes so a future
    # "dark-mode" subclass could rebrand without touching render code.
    _FACE_FILL = "#ffffff"
    _FACE_STROKE = "#000"
    _FACE_STROKE_WIDTH = 2.0
    _HOUR_TICK_STROKE_WIDTH = 2.0
    _MINUTE_TICK_STROKE_WIDTH = 1.0
    _HOUR_HAND_STROKE_WIDTH = 3.0
    _MINUTE_HAND_STROKE_WIDTH = 2.0
    _HUB_RADIUS = 2.0
    _NUMERAL_FONT_SIZE = 14

    # Geometric ratios. Centralised so the SVG and TikZ paths stay in
    # lockstep — if we shorten the hour hand we want both formats to
    # update together.
    _HOUR_HAND_FRACTION = 0.50
    _MINUTE_HAND_FRACTION = 0.75
    _HOUR_TICK_INNER = 0.85   # tick runs from 0.85·r out to r
    _MINUTE_TICK_INNER = 0.92  # thinner tick, runs from 0.92·r out to r
    _NUMERAL_RADIUS_FRACTION = 0.72  # where the "1"-"12" labels sit

    def __init__(
        self,
        hour: int,
        minute: int = 0,
        radius: float = 80,
        show_minute_marks: bool = True,
        width: int = 200,
        height: int = 200,
    ):
        super().__init__(width=width, height=height)

        # ---- input validation ------------------------------------------------
        # Negative inputs are always errors — there is no sensible
        # "negative hour" or "negative minute" to render.
        if hour < 0:
            raise ValueError(f"hour must be >= 0, got {hour}")
        if minute < 0:
            raise ValueError(f"minute must be >= 0, got {minute}")
        if radius <= 0:
            raise ValueError(f"radius must be > 0, got {radius}")

        # ---- minute rollover -------------------------------------------------
        # ``minute == 60`` is a common author convenience — they want
        # "the top of the next hour" without having to bump the hour
        # themselves. Anything > 60 is suspicious and we reject it
        # so callers don't accidentally pass minute-of-day.
        if minute == 60:
            hour += 1
            minute = 0
        if not (0 <= minute < 60):
            raise ValueError(f"minute must be in [0, 60], got {minute}")

        # ---- hour wrap -------------------------------------------------------
        # 0 → 12, 13 → 1, etc. The internal canonical form is 1-12 so
        # the rendering helpers don't need to special-case 0.
        hour = hour % 12
        if hour == 0:
            hour = 12

        self.hour = hour
        self.minute = minute
        self.radius = float(radius)
        self.show_minute_marks = bool(show_minute_marks)

    # ------------------------------------------------------------------
    # Geometry helpers
    # ------------------------------------------------------------------

    def _center(self) -> Tuple[float, float]:
        """SVG-space coordinates of the face centre."""
        return (self.width / 2, self.height / 2)

    def _polar_clock(self, clock_deg: float, r: float) -> Tuple[float, float]:
        """Convert a clock-face angle (0° = up, CW) at distance ``r`` to SVG (x, y).

        Clock convention has 0° at 12 o'clock and rotates clockwise. We
        rewrite as math-convention (CCW from +x) by ``θ_math = 90° −
        θ_clock`` and then SVG-flip y. This single helper drives every
        tick, numeral, and hand endpoint, so the rotation offset is
        applied in exactly one place.
        """
        cx, cy = self._center()
        math_deg = 90.0 - clock_deg
        rad = math.radians(math_deg)
        return (cx + r * math.cos(rad), cy - r * math.sin(rad))

    def _hour_hand_angle(self) -> float:
        """Clock-face angle (deg) of the hour hand.

        The hour hand advances continuously: at 3:30 it sits halfway
        between the 3 and the 4, not exactly on the 3. ``hour % 12``
        keeps 12 mapped to 0° (straight up) so the hand points at the
        12 numeral when minutes are 0.
        """
        return ((self.hour % 12) + self.minute / 60.0) * 30.0

    def _minute_hand_angle(self) -> float:
        """Clock-face angle (deg) of the minute hand. 6° per minute."""
        return self.minute * 6.0

    # ------------------------------------------------------------------
    # to_svg
    # ------------------------------------------------------------------

    def to_svg(self) -> str:
        cx, cy = self._center()
        r = self.radius
        parts: List[str] = []

        # Outer face — filled white, black stroke. White (rather than
        # ``none``) so the minute-tick layer below the rim doesn't show
        # through if a parent template stacks visuals.
        parts.append(
            f'<circle cx="{_fmt(cx)}" cy="{_fmt(cy)}" r="{_fmt(r)}" '
            f'fill="{self._FACE_FILL}" stroke="{self._FACE_STROKE}" '
            f'stroke-width="{_fmt(self._FACE_STROKE_WIDTH)}"/>'
        )

        # Minute tick marks (thin, 60 of them) — drawn first so the
        # thicker hour ticks paint over them at the dodecant positions.
        if self.show_minute_marks:
            for m in range(60):
                # Skip positions that already have an hour tick — they'd
                # otherwise be drawn twice with different stroke widths
                # and cause anti-aliasing fringes.
                if m % 5 == 0:
                    continue
                angle = m * 6.0
                x1, y1 = self._polar_clock(angle, r * self._MINUTE_TICK_INNER)
                x2, y2 = self._polar_clock(angle, r)
                parts.append(
                    f'<line x1="{_fmt(x1)}" y1="{_fmt(y1)}" '
                    f'x2="{_fmt(x2)}" y2="{_fmt(y2)}" '
                    f'stroke="{self._FACE_STROKE}" '
                    f'stroke-width="{_fmt(self._MINUTE_TICK_STROKE_WIDTH)}"/>'
                )

        # Hour tick marks (thicker, 12 of them).
        for h in range(12):
            angle = h * 30.0
            x1, y1 = self._polar_clock(angle, r * self._HOUR_TICK_INNER)
            x2, y2 = self._polar_clock(angle, r)
            parts.append(
                f'<line x1="{_fmt(x1)}" y1="{_fmt(y1)}" '
                f'x2="{_fmt(x2)}" y2="{_fmt(y2)}" '
                f'stroke="{self._FACE_STROKE}" '
                f'stroke-width="{_fmt(self._HOUR_TICK_STROKE_WIDTH)}"/>'
            )

        # Hour numerals 1-12. Numeral ``n`` sits at clock-angle ``n·30°``
        # (so 12 is at 360° == 0° == top, 3 at 90° == right, etc).
        # ``dominant-baseline="central"`` plus ``text-anchor="middle"``
        # centres the glyph on the polar coordinate so different
        # multi-digit widths (1 vs 12) line up tidily.
        for n in range(1, 13):
            angle = n * 30.0
            tx, ty = self._polar_clock(angle, r * self._NUMERAL_RADIUS_FRACTION)
            parts.append(
                f'<text x="{_fmt(tx)}" y="{_fmt(ty)}" '
                f'text-anchor="middle" dominant-baseline="central" '
                f'font-family="Times New Roman, Times, serif" '
                f'font-size="{self._NUMERAL_FONT_SIZE}">'
                f'{_esc(str(n))}</text>'
            )

        # Hour hand. Endpoint computed via the same polar helper so it
        # respects the 90° clock→math offset without per-call fudging.
        hh_angle = self._hour_hand_angle()
        hx, hy = self._polar_clock(hh_angle, r * self._HOUR_HAND_FRACTION)
        parts.append(
            f'<line x1="{_fmt(cx)}" y1="{_fmt(cy)}" '
            f'x2="{_fmt(hx)}" y2="{_fmt(hy)}" '
            f'stroke="{self._FACE_STROKE}" '
            f'stroke-width="{_fmt(self._HOUR_HAND_STROKE_WIDTH)}" '
            f'stroke-linecap="round"/>'
        )

        # Minute hand — longer, thinner.
        mh_angle = self._minute_hand_angle()
        mx, my = self._polar_clock(mh_angle, r * self._MINUTE_HAND_FRACTION)
        parts.append(
            f'<line x1="{_fmt(cx)}" y1="{_fmt(cy)}" '
            f'x2="{_fmt(mx)}" y2="{_fmt(my)}" '
            f'stroke="{self._FACE_STROKE}" '
            f'stroke-width="{_fmt(self._MINUTE_HAND_STROKE_WIDTH)}" '
            f'stroke-linecap="round"/>'
        )

        # Centre hub — a small filled disc at the rotation pivot. Drawn
        # last so it hides the rough end-of-line where the two hands
        # meet at the centre.
        parts.append(
            f'<circle cx="{_fmt(cx)}" cy="{_fmt(cy)}" '
            f'r="{_fmt(self._HUB_RADIUS)}" fill="{self._FACE_STROKE}"/>'
        )

        return self._wrap(*parts)

    # ------------------------------------------------------------------
    # to_text
    # ------------------------------------------------------------------

    def to_text(self) -> str:
        """One-paragraph ASCII description.

        Format is ``Clock showing H:MM.`` — minutes always zero-padded
        so downstream regex matchers / dataset consumers don't have to
        special-case the single-digit case.
        """
        return f"Clock showing {self.hour}:{self.minute:02d}."

    # ------------------------------------------------------------------
    # to_latex (TikZ)
    # ------------------------------------------------------------------

    def to_latex(self) -> str:
        """TikZ rendering.

        TikZ uses standard math angle convention (0° = +x, CCW), so
        each clock-face angle is rewritten with the same ``90° −
        θ_clock`` offset used in ``_polar_clock``. The result is a
        compact ``tikzpicture`` with one ``\\draw circle``, twelve
        numeral nodes, and two hand lines. Radius is converted to
        centimetres (SVG units / 20) so the figure fits a printed
        page without overflow.
        """
        # SVG → TikZ unit conversion. 20 SVG-units ≈ 1 cm matches the
        # convention shared with ``SectorFigure.to_latex``.
        r_cm = self.radius / 20.0
        r_str = _fmt(r_cm)

        lines: List[str] = []
        lines.append(r"\begin{tikzpicture}")
        # Outer face. ``thick`` matches the ~2px SVG stroke.
        lines.append(rf"  \draw[thick] (0,0) circle ({r_str});")

        # Hour tick marks — short black radial segments.
        for h in range(12):
            clock_deg = h * 30.0
            math_deg = 90.0 - clock_deg
            inner_str = _fmt(r_cm * self._HOUR_TICK_INNER)
            outer_str = _fmt(r_cm)
            angle_str = _fmt(math_deg)
            lines.append(
                rf"  \draw[thick] ({angle_str}:{inner_str}) -- "
                rf"({angle_str}:{outer_str});"
            )

        # Optional minute tick marks. We skip multiples of 5 because
        # those positions already get the (thicker) hour tick above.
        if self.show_minute_marks:
            for m in range(60):
                if m % 5 == 0:
                    continue
                clock_deg = m * 6.0
                math_deg = 90.0 - clock_deg
                inner_str = _fmt(r_cm * self._MINUTE_TICK_INNER)
                outer_str = _fmt(r_cm)
                angle_str = _fmt(math_deg)
                lines.append(
                    rf"  \draw ({angle_str}:{inner_str}) -- "
                    rf"({angle_str}:{outer_str});"
                )

        # Hour numerals 1-12 via ``\node at (math-angle:radius)``.
        numeral_r = _fmt(r_cm * self._NUMERAL_RADIUS_FRACTION)
        for n in range(1, 13):
            clock_deg = n * 30.0
            math_deg = 90.0 - clock_deg
            angle_str = _fmt(math_deg)
            lines.append(
                rf"  \node at ({angle_str}:{numeral_r}) "
                rf"{{{_latex_escape(str(n))}}};"
            )

        # Hour hand.
        hh_clock = self._hour_hand_angle()
        hh_math = 90.0 - hh_clock
        hh_len = _fmt(r_cm * self._HOUR_HAND_FRACTION)
        lines.append(
            rf"  \draw[very thick] (0,0) -- ({_fmt(hh_math)}:{hh_len});"
        )

        # Minute hand.
        mh_clock = self._minute_hand_angle()
        mh_math = 90.0 - mh_clock
        mh_len = _fmt(r_cm * self._MINUTE_HAND_FRACTION)
        lines.append(
            rf"  \draw[thick] (0,0) -- ({_fmt(mh_math)}:{mh_len});"
        )

        # Centre hub.
        lines.append(r"  \fill (0,0) circle (0.1);")
        lines.append(r"\end{tikzpicture}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # render() — keeps the visual-sandbox `Visual = ...` contract
    # ------------------------------------------------------------------

    def render(self) -> str:
        return self.to_svg()
