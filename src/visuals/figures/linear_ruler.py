"""γ.4s — :class:`LinearRuler`: K1 measurement-by-units visual.

K1 ``measurement.length`` templates pose questions of the form:

    "An eraser is laid alongside a row of cubes. How many cubes long
    is the eraser?"

The visual is two parallel horizontal rows: the *measured object*
(eraser, pencil, stick — a single bar) on top, and a row of *unit
cells* (cubes / clips / paperclips) underneath, with the unit row
acting as the implicit ruler. The student counts the units to read
the length off the diagram. The cube-count is the answer.

Layout invariant
----------------

The object bar's left edge **aligns horizontally** with the unit
row's left edge, and the bar's width is exactly
``object_length_units * unit_size``. That alignment plus equal width
is what lets the student answer "how many cubes long" by direct
visual comparison — drift would lie about the answer.

Multi-format rendering follows the γ.3 keystone contract:

- :meth:`to_svg` — self-contained SVG (also returned by
  :meth:`render`).
- :meth:`to_text` — one-line ASCII description.
- :meth:`to_latex` — real TikZ (two horizontal rows of rectangles).

Determinism: same constructor args → byte-identical SVG.
Coordinates flow through :func:`_fmt` which strips trailing zeros
so renderers don't shift the byte stream out from under the
fixture-drift lint.
"""

from __future__ import annotations

from typing import List

from ..base import DEFAULT_FONT, SVGBuilder, _esc, _fmt, _latex_escape
from .shape_glyph import _GLYPH_MAP, glyph_for


class LinearRuler(SVGBuilder):
    """Two-row "object-vs-units" measurement visual for K1.

    Parameters
    ----------
    object_length_units:
        Length of the measured object expressed in units. Equals the
        number of unit-cells drawn beneath the bar — and equals the
        answer to the spoken question. Must be ``>= 0``; ``0`` is a
        legal degenerate case (zero-length object, empty unit row),
        useful for "how many do you need to start?" framing.
    unit_item:
        Plural prose name of the unit being used. Drives the
        rendering of each unit cell:

        - ``"cubes"`` / ``"blocks"`` / ``"cube"`` / ``"block"`` →
          rounded-rect glyph via :func:`glyph_for` (the canonical
          K1 cube).
        - ``"clips"`` / ``"paperclips"`` (and singular forms) →
          custom horizontal pill-shape (rect with rounded ends),
          rendered narrow because clips read as "stretched"
          horizontally.
        - Anything else → plain filled square in ``unit_color``.
    object_label:
        Prose label for the measured object (``"eraser"``,
        ``"pencil"``, ``"stick"``). Drawn centred above the bar.
    object_color:
        Fill colour for the object bar. Default amber so the bar
        contrasts the blue unit row.
    unit_color:
        Fallback fill for unit cells when ``unit_item`` doesn't
        match any specialised renderer.
    width, height:
        SVG viewport. Default 480×140 fits two rows comfortably with
        room above for the object label.

    Raises
    ------
    ValueError
        If ``object_length_units < 0``.
    """

    # Visual constants — class-level so subclasses can rebrand.
    _STROKE = "#000"
    _STROKE_WIDTH = 1.5
    _MARGIN = 16  # left / right padding inside the SVG viewport
    _MIN_CELLS_FOR_AUTO_SIZE = 12  # default sizing target — keeps small counts roomy
    _MAX_CELL_SIZE = 40  # never render a cell larger than this

    # Vertical placement (per spec):
    #  - object bar:  y ≈ 30..60  (label above at ≈ 22)
    #  - unit row:    y ≈ 80..120 (centred when cells smaller than band)
    _LABEL_Y = 22
    _OBJECT_Y = 30
    _OBJECT_HEIGHT = 30
    _UNITS_BAND_Y = 80
    _UNITS_BAND_HEIGHT = 40

    def __init__(
        self,
        object_length_units: int,
        unit_item: str = "cubes",
        object_label: str = "eraser",
        object_color: str = "#fbbf24",
        unit_color: str = "#60a5fa",
        width: int = 480,
        height: int = 140,
    ):
        super().__init__(width=width, height=height)
        if object_length_units < 0:
            raise ValueError(
                f"object_length_units must be >= 0, got {object_length_units}"
            )
        self.object_length_units = int(object_length_units)
        self.unit_item = str(unit_item)
        self.object_label = str(object_label)
        self.object_color = object_color
        self.unit_color = unit_color

        # Compute unit_size from the wider of (actual count) and a
        # minimum-cell-count target so a 3-cube ruler doesn't render
        # with absurdly fat 100px cubes. This mirrors the spec:
        # "default unit_size = (width - 2*margin) / max(N, 12)".
        available = max(1, self.width - 2 * self._MARGIN)
        denom = max(self.object_length_units, self._MIN_CELLS_FOR_AUTO_SIZE)
        self.unit_size = min(available / denom, float(self._MAX_CELL_SIZE))

    # ------------------------------------------------------------------
    # Layout helpers
    # ------------------------------------------------------------------

    def _strip_origin_x(self) -> float:
        """X coordinate of the unit-row left edge.

        Centres the row of N unit cells inside the viewport. The
        object bar inherits this same x so the alignment invariant
        holds (left edges flush).
        """
        total_w = self.unit_size * self.object_length_units
        return (self.width - total_w) / 2

    def _bar_width(self) -> float:
        """Width of the object bar — exactly N * unit_size.

        Special-case: a zero-length object renders at a tiny visible
        nub (4 px) so it doesn't disappear; ``to_text`` flags the
        edge case textually.
        """
        if self.object_length_units == 0:
            return 4.0
        return self.unit_size * self.object_length_units

    def _bar_origin_x(self) -> float:
        """X coordinate of the object bar's left edge.

        For ``object_length_units >= 1`` this equals
        :meth:`_strip_origin_x` — same left edge as the unit row, so
        the visual measurement reads true. For the zero-length edge
        case we centre the nub on the empty unit row's centreline
        (which collapses to width/2 since the row has 0 width).
        """
        if self.object_length_units == 0:
            return self.width / 2 - 2.0
        return self._strip_origin_x()

    # ------------------------------------------------------------------
    # Unit-cell rendering dispatch
    # ------------------------------------------------------------------

    def _is_glyph_unit(self) -> bool:
        """True when ``unit_item`` is a known shape_glyph entry.

        Cubes / blocks / boxes etc. fall through to ``glyph_for``
        which renders a rounded-rect — the canonical "unit cube".
        """
        return self.unit_item.strip().lower() in _GLYPH_MAP

    def _is_clip_unit(self) -> bool:
        """True when ``unit_item`` is a paperclip-style item.

        Clips render as a narrow horizontal pill rather than a
        square — they read as stretched in real life.
        """
        key = self.unit_item.strip().lower()
        return key in {"clip", "clips", "paperclip", "paperclips"}

    def _render_unit_cell_svg(self, cx: float, cy: float) -> str:
        """SVG snippet for a single unit cell, dispatching by item.

        Cubes use ``glyph_for`` (rounded_rect glyph). Clips use a
        local pill renderer. Anything else falls back to a plain
        filled square in ``unit_color``.
        """
        cs = self.unit_size
        if self._is_clip_unit():
            # Pill: width ≈ cs * 0.95, height ≈ cs * 0.45 → reads as
            # a paperclip silhouette laid horizontally.
            w = cs * 0.95
            h = cs * 0.45
            x = cx - w / 2
            y = cy - h / 2
            return (
                f'<rect x="{_fmt(x)}" y="{_fmt(y)}" '
                f'width="{_fmt(w)}" height="{_fmt(h)}" '
                f'rx="{_fmt(h / 2)}" ry="{_fmt(h / 2)}" '
                f'fill="{self.unit_color}" stroke="{self._STROKE}" '
                f'stroke-width="1"/>'
            )
        if self._is_glyph_unit():
            # Glyph diameter at 80% of cs leaves a small breathing
            # gap between adjacent cubes so the count reads cleanly.
            glyph = glyph_for(self.unit_item)
            return glyph(cx, cy, cs * 0.85, self.unit_color)
        # Fallback: plain square cell.
        x = cx - cs / 2
        y = cy - cs / 2
        side = cs * 0.85
        return (
            f'<rect x="{_fmt(cx - side / 2)}" y="{_fmt(cy - side / 2)}" '
            f'width="{_fmt(side)}" height="{_fmt(side)}" '
            f'fill="{self.unit_color}" stroke="{self._STROKE}" '
            f'stroke-width="1"/>'
        )

    # ------------------------------------------------------------------
    # to_svg
    # ------------------------------------------------------------------

    def to_svg(self) -> str:
        parts: List[str] = []

        # Object label — centred above the bar.
        bar_x = self._bar_origin_x()
        bar_w = self._bar_width()
        bar_cx = bar_x + bar_w / 2
        parts.append(
            f'<text x="{_fmt(bar_cx)}" y="{_fmt(self._LABEL_Y)}" '
            f'text-anchor="middle" {DEFAULT_FONT}>'
            f'{_esc(self.object_label)}</text>'
        )

        # Object bar.
        parts.append(
            f'<rect x="{_fmt(bar_x)}" y="{_fmt(self._OBJECT_Y)}" '
            f'width="{_fmt(bar_w)}" height="{_fmt(self._OBJECT_HEIGHT)}" '
            f'fill="{self.object_color}" stroke="{self._STROKE}" '
            f'stroke-width="{_fmt(self._STROKE_WIDTH)}"/>'
        )

        # Unit row — N cells of width `unit_size`, centred vertically
        # in the units band. (Cell vertical extent is `unit_size`; the
        # band is fixed-height so cells smaller than the band sit
        # mid-band rather than glued to the top.)
        if self.object_length_units > 0:
            x0 = self._strip_origin_x()
            cy = self._UNITS_BAND_Y + self._UNITS_BAND_HEIGHT / 2
            for i in range(self.object_length_units):
                cx = x0 + i * self.unit_size + self.unit_size / 2
                parts.append(self._render_unit_cell_svg(cx, cy))

        return self._wrap(*parts)

    # ------------------------------------------------------------------
    # to_text
    # ------------------------------------------------------------------

    def to_text(self) -> str:
        """One-line ASCII description.

        Examples::

            "An eraser laid alongside a row of 8 cubes."
            "A pencil laid alongside a row of 5 clips."

        Zero-length flags the degenerate case so screen-readers /
        alt-text don't say "alongside a row of 0 cubes" without
        context.
        """
        if self.object_length_units == 0:
            return (
                f"A {self.object_label} laid alongside an empty row of "
                f"{self.unit_item} (length 0)."
            )
        article = "An" if self.object_label[:1].lower() in "aeiou" else "A"
        return (
            f"{article} {self.object_label} laid alongside a row of "
            f"{self.object_length_units} {self.unit_item}."
        )

    # ------------------------------------------------------------------
    # to_latex (TikZ)
    # ------------------------------------------------------------------

    def to_latex(self) -> str:
        """TikZ rendering — two horizontal rows of rectangles.

        Standard case ships real TikZ rather than the
        ``\\fbox{[Figure: ...]}`` fallback: the visual is just
        rectangles and a label, both of which TikZ handles natively.
        Cubes / clips / unknowns all degrade to a labelled rectangle
        in TikZ — the geometric shape is the same, only the SVG fill
        differs across the three; the LaTeX surface keeps the figure
        legible without trying to reproduce six glyphs.
        """
        # 20 SVG-units ≈ 1 cm — same scale used by SectorFigure /
        # PatternStrip so a multi-figure dataset renders consistently.
        cs_cm = self.unit_size / 20.0
        n = self.object_length_units
        bar_w_cm = max(cs_cm * n, 0.2)  # match the SVG zero-length nub
        cs_str = _fmt(cs_cm)
        bar_w_str = _fmt(bar_w_cm)

        lines: List[str] = [r"\begin{tikzpicture}"]
        # Object bar — row at y = 1.5 cm (above the unit row).
        lines.append(
            rf"  \draw[fill=orange!50] "
            rf"(0,1.5) rectangle ({bar_w_str},2.3);"
        )
        # Object label centred above the bar.
        bar_cx_str = _fmt(bar_w_cm / 2)
        lines.append(
            rf"  \node[above] at ({bar_cx_str},2.3) "
            rf"{{{_latex_escape(self.object_label)}}};"
        )
        # Unit row — n adjacent rectangles at y in [0, cs_cm].
        for i in range(n):
            x_str = _fmt(i * cs_cm)
            x_right_str = _fmt((i + 1) * cs_cm)
            top_str = _fmt(cs_cm)
            lines.append(
                rf"  \draw[fill=blue!20] "
                rf"({x_str},0) rectangle ({x_right_str},{top_str});"
            )
        lines.append(r"\end{tikzpicture}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # render() default — visual-sandbox `Visual = ...` contract
    # ------------------------------------------------------------------

    def render(self) -> str:
        return self.to_svg()
