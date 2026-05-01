"""γ.4s — :class:`PatternStrip`: horizontal cell-strip for K1 pattern problems.

K1 pattern-recognition templates ("what comes next?", "fill in the
missing number", "ABAB pattern") all share the same visual: a single
row of N cells, each cell containing either a glyph (apples, books,
stars) or a textual label (a number, a word), with optional cells
left blank as a missing-cell prompt for the student to identify.

This builder produces that strip. Cells share borders so the figure
reads as a continuous tape, and each cell content is dispatched by
type:

- ``str`` whose lower-case form is in :data:`shape_glyph._GLYPH_MAP`
  → glyph drawn at cell centre (``glyph_for(name)``).
- ``str`` not matching any glyph → centred text label (treated as
  a word, e.g. ``"red"``, ``"Mon"``, ``"+5"``).
- ``int`` → centred numeric text label (skip-counting and number-
  strip patterns: ``[2, 4, None, 8, 10]``).
- ``None`` → cell rendered with ``missing_fill`` background and a
  centred ``"?"`` glyph; this is the "what goes here?" prompt.

Multi-format rendering follows the γ.3 keystone contract:

- :meth:`to_svg` — self-contained SVG (also returned by
  :meth:`render`).
- :meth:`to_text` — one-line ASCII description listing the cells in
  order, with ``?`` substituted for missing cells.
- :meth:`to_latex` — real TikZ when reasonable; cells lay out
  cleanly as a horizontal stack of rectangles with embedded
  ``\\node`` text.

Determinism: same constructor args → byte-identical SVG. Coordinates
flow through :func:`_fmt` which strips trailing zeros.
"""

from __future__ import annotations

from typing import List, Optional, Union

from ..base import DEFAULT_FONT, SVGBuilder, _esc, _fmt, _latex_escape
from .shape_glyph import _GLYPH_MAP, glyph_for


# A cell is one of: a string (glyph item-name or text label), an
# integer (rendered as text), or None (missing-cell prompt).
Cell = Union[str, int, None]


class PatternStrip(SVGBuilder):
    """Horizontal sequence of cells for K1 pattern problems.

    Parameters
    ----------
    cells:
        List of cell contents. Each entry is ``str``, ``int``, or
        ``None`` (see module docstring for dispatch rules). Empty
        list is allowed and renders as a blank canvas.
    cell_size:
        Preferred cell side length in SVG units. Auto-shrinks to
        keep the strip inside ``width - 2*margin`` when there are
        many cells.
    cell_fill:
        Background colour for normal cells.
    missing_fill:
        Background colour for ``None`` cells. Different default
        (yellow vs. blue) so missing cells pop visually for K1
        readers.
    width, height:
        SVG viewport. ``height`` is fixed; cell size auto-shrinks
        independently of viewport so the row stays vertically
        centred whatever the cell count.
    """

    # Visual constants. Class-level so subclasses can rebrand.
    _STROKE = "#000"
    _STROKE_WIDTH = 1.0
    _MARGIN = 16  # left / right padding inside the SVG viewport
    _GLYPH_FRACTION = 0.55  # glyph diameter as fraction of cell_size
    _FONT_FRACTION = 0.45  # text font-size as fraction of cell_size
    _MISSING_FONT_FRACTION = 0.55  # "?" runs slightly larger

    def __init__(
        self,
        cells: Optional[List[Cell]] = None,
        cell_size: float = 48,
        cell_fill: str = "#dbeafe",
        missing_fill: str = "#fde68a",
        width: int = 480,
        height: int = 80,
    ):
        super().__init__(width=width, height=height)
        self.cells: List[Cell] = list(cells) if cells else []
        self.cell_fill = cell_fill
        self.missing_fill = missing_fill

        # Auto-shrink: if requested cell_size × N exceeds the
        # available width (viewport minus margins), reduce cell_size
        # so the strip fits. Authors who care about pixel-perfect
        # cells should pass a wider viewport instead — but the strip
        # never overflows.
        self._requested_cell_size = float(cell_size)
        n = len(self.cells)
        if n > 0:
            available = max(1, self.width - 2 * self._MARGIN)
            if self._requested_cell_size * n > available:
                self.cell_size = available / n
            else:
                self.cell_size = self._requested_cell_size
        else:
            self.cell_size = self._requested_cell_size

    # ------------------------------------------------------------------
    # Dispatch helpers
    # ------------------------------------------------------------------

    def _cell_kind(self, cell: Cell) -> str:
        """Classify a cell into 'glyph' / 'text' / 'missing'.

        Centralised so SVG / text / LaTeX renderers all agree on what
        a given cell *is*, regardless of the surface they emit.
        """
        if cell is None:
            return "missing"
        if isinstance(cell, int) and not isinstance(cell, bool):
            return "text"
        if isinstance(cell, str):
            key = cell.strip().lower()
            if key in _GLYPH_MAP:
                return "glyph"
            return "text"
        # Anything else (floats, exotic types) → text fallback so we
        # don't crash on a future caller passing a non-canonical type.
        return "text"

    def _cell_text(self, cell: Cell) -> str:
        """ASCII representation of a cell for to_text / fallback."""
        if cell is None:
            return "?"
        return str(cell)

    # ------------------------------------------------------------------
    # Layout helpers
    # ------------------------------------------------------------------

    def _strip_origin(self) -> tuple[float, float]:
        """Top-left corner of the strip — centred in the viewport."""
        n = len(self.cells)
        total_w = self.cell_size * n
        x0 = (self.width - total_w) / 2
        y0 = (self.height - self.cell_size) / 2
        return (x0, y0)

    # ------------------------------------------------------------------
    # to_svg
    # ------------------------------------------------------------------

    def to_svg(self) -> str:
        parts: List[str] = []
        if not self.cells:
            return self._wrap(*parts)

        x0, y0 = self._strip_origin()
        cs = self.cell_size

        for i, cell in enumerate(self.cells):
            kind = self._cell_kind(cell)
            cx = x0 + i * cs + cs / 2
            cy = y0 + cs / 2
            x = x0 + i * cs

            # Background rect for the cell — shared borders, so we
            # always emit one rect per cell; adjacent strokes overlap
            # cleanly at 1px width.
            fill = self.missing_fill if kind == "missing" else self.cell_fill
            parts.append(
                f'<rect x="{_fmt(x)}" y="{_fmt(y0)}" '
                f'width="{_fmt(cs)}" height="{_fmt(cs)}" '
                f'fill="{fill}" stroke="{self._STROKE}" '
                f'stroke-width="{_fmt(self._STROKE_WIDTH)}"/>'
            )

            # Cell content.
            if kind == "glyph":
                glyph = glyph_for(str(cell))
                glyph_size = cs * self._GLYPH_FRACTION
                parts.append(glyph(cx, cy, glyph_size, "#fb923c"))
            elif kind == "missing":
                font_size = cs * self._MISSING_FONT_FRACTION
                # SVG <text> y is the baseline — offset by ~0.35×fs to
                # vertically centre most glyphs reasonably across
                # renderers.
                ty = cy + font_size * 0.35
                parts.append(
                    f'<text x="{_fmt(cx)}" y="{_fmt(ty)}" '
                    f'text-anchor="middle" '
                    f'font-family="Times New Roman, Times, serif" '
                    f'font-size="{_fmt(font_size)}" '
                    f'font-weight="bold">?</text>'
                )
            else:  # text
                font_size = cs * self._FONT_FRACTION
                ty = cy + font_size * 0.35
                parts.append(
                    f'<text x="{_fmt(cx)}" y="{_fmt(ty)}" '
                    f'text-anchor="middle" '
                    f'font-family="Times New Roman, Times, serif" '
                    f'font-size="{_fmt(font_size)}">'
                    f'{_esc(self._cell_text(cell))}</text>'
                )

        return self._wrap(*parts)

    # ------------------------------------------------------------------
    # to_text
    # ------------------------------------------------------------------

    def to_text(self) -> str:
        """One-line ASCII description.

        Title chosen by majority cell-kind: predominantly numeric
        cells → "Number strip"; predominantly glyph cells → "Shape
        strip"; otherwise → "Pattern strip". This is purely cosmetic
        for alt-text / screen readers — the cell list itself is
        always reported verbatim.
        """
        if not self.cells:
            return "Pattern strip: (empty)."
        kinds = [self._cell_kind(c) for c in self.cells]
        non_missing = [k for k in kinds if k != "missing"]
        if non_missing and all(
            isinstance(c, int) and not isinstance(c, bool)
            for c, k in zip(self.cells, kinds) if k != "missing"
        ):
            title = "Number strip"
        elif non_missing and all(k == "glyph" for k in non_missing):
            title = "Shape strip"
        else:
            title = "Pattern strip"
        body = ", ".join(self._cell_text(c) for c in self.cells)
        return f"{title}: {body}."

    # ------------------------------------------------------------------
    # to_latex (TikZ)
    # ------------------------------------------------------------------

    def to_latex(self) -> str:
        """TikZ rendering.

        A horizontal row of ``\\draw`` rectangles, each with a
        centred ``\\node`` for content. Glyph cells degrade to a
        textual placeholder (the item name in italics) — TikZ shape
        primitives can't reproduce all six glyphs faithfully, and a
        word label is the standard accessibility fallback already
        used in to_text. Missing cells render as a shaded rectangle
        with a bold ``?``. Empty strip returns an empty
        ``tikzpicture`` envelope.
        """
        cs_cm = self.cell_size / 20.0  # 20 SVG-units ≈ 1 cm
        cs_str = _fmt(cs_cm)
        lines: List[str] = [r"\begin{tikzpicture}"]

        for i, cell in enumerate(self.cells):
            kind = self._cell_kind(cell)
            x = i * cs_cm
            x_str = _fmt(x)
            x_right_str = _fmt(x + cs_cm)
            y_top_str = _fmt(cs_cm)
            cx_str = _fmt(x + cs_cm / 2)
            cy_str = _fmt(cs_cm / 2)

            if kind == "missing":
                # Shaded rectangle — TikZ's "fill=yellow!30" is a
                # close visual analogue to the SVG `missing_fill`.
                lines.append(
                    rf"  \draw[fill=yellow!30] "
                    rf"({x_str},0) rectangle ({x_right_str},{y_top_str});"
                )
                lines.append(
                    rf"  \node[font=\bfseries] at ({cx_str},{cy_str}) {{?}};"
                )
            else:
                lines.append(
                    rf"  \draw[fill=blue!10] "
                    rf"({x_str},0) rectangle ({x_right_str},{y_top_str});"
                )
                if kind == "glyph":
                    label = rf"\textit{{{_latex_escape(str(cell))}}}"
                else:
                    label = _latex_escape(self._cell_text(cell))
                lines.append(
                    rf"  \node at ({cx_str},{cy_str}) {{{label}}};"
                )

        lines.append(r"\end{tikzpicture}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # render() default — keeps the visual-sandbox `Visual = ...`
    # contract identical to other γ.3 / γ.4s figures.
    # ------------------------------------------------------------------

    def render(self) -> str:
        return self.to_svg()
