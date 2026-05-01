"""γ A.1 (TableSVG): 2D-table builder with multi-target output.

Function-value tables (Riemann sums, derivative checks), matrix
displays (eigenvalue problems), and general data tables (sample
data summaries) all share the same underlying layout —
header row + grid of cells, optional caption, optional cell
highlights. The shipping variants are thin subclasses that just
fix the constructor signature; everything else lives on the base.

Per the Phase γ keystone constraint, every render path goes through
:class:`TableSVG` so the same table looks the same across the four
output formats:

- :meth:`to_svg` — SVG markup with grid lines, header tinting, optional
  caption banner, optional cell highlights.
- :meth:`to_text` — Unicode box-drawing characters
  (``┌`` / ``─`` / ``│`` / ...) — readable in a terminal `less`.
- :meth:`to_markdown` — GFM pipe-table.
- :meth:`to_latex` — ``tabular`` environment.

``render()`` defaults to ``to_svg()`` so the existing visual sandbox
contract (a ``Visual = builder.render()`` binding produces an SVG
string) keeps working without any changes in the renderer pipeline.

Numeric vs. non-numeric columns are detected per-column by sampling
the first non-empty cell; numeric columns get a monospace font in
SVG and right-alignment in markdown/LaTeX so a Riemann-sum table
with f(x) values aligned on the decimal point reads cleanly.
"""

from __future__ import annotations

from typing import Any, List, Optional, Sequence, Tuple

from .base import SVGBuilder, _esc, _fmt, _latex_escape


# Column-alignment values accepted from authors.
_VALID_ALIGN = ("left", "center", "right")


class TableSVG(SVGBuilder):
    """Generic table builder. See module docstring for the four render targets."""

    # SVG layout knobs. Authors override via constructor when defaults
    # don't fit (e.g. a wide function-value table needs extra horizontal
    # padding for long y values like "1.41421356").
    _ROW_HEIGHT = 28
    _HEADER_HEIGHT = 32
    _CAPTION_HEIGHT = 24
    _CELL_PADDING_X = 12
    _GRID_STROKE = "#666"
    _HEADER_FILL = "#eef2f7"
    _HIGHLIGHT_FILL = "#fff7c2"

    def __init__(
        self,
        headers: Sequence[str],
        rows: Sequence[Sequence[Any]],
        *,
        caption: Optional[str] = None,
        highlights: Optional[Sequence[Tuple[int, int]]] = None,
        align: Optional[Sequence[str]] = None,
        width: int = 480,
        col_widths: Optional[Sequence[int]] = None,
    ):
        self.headers: List[str] = [str(h) for h in headers]
        self.rows: List[List[str]] = [
            [self._cell_str(v) for v in row] for row in rows
        ]
        self._validate_shape()

        self.caption = caption
        self.highlights = list(highlights or [])

        n_cols = len(self.headers)
        if align is None:
            align = ["right" if self._col_is_numeric(i) else "left"
                     for i in range(n_cols)]
        if len(align) != n_cols:
            raise ValueError(
                f"align: expected {n_cols} entries, got {len(align)}"
            )
        for a in align:
            if a not in _VALID_ALIGN:
                raise ValueError(
                    f"align entry {a!r} not in {_VALID_ALIGN}"
                )
        self.align: List[str] = list(align)

        if col_widths is None:
            col_widths = self._auto_col_widths(width)
        self.col_widths: List[int] = list(col_widths)
        if len(self.col_widths) != n_cols:
            raise ValueError(
                f"col_widths: expected {n_cols} entries, "
                f"got {len(self.col_widths)}"
            )

        # Recompute final width from the column widths so the SVG
        # viewBox tracks the actual table extent (keeps cell strokes
        # inside the viewport even when col_widths was overridden).
        total_w = sum(self.col_widths)
        n_rows = len(self.rows)
        cap_h = self._CAPTION_HEIGHT if self.caption else 0
        total_h = cap_h + self._HEADER_HEIGHT + n_rows * self._ROW_HEIGHT
        super().__init__(width=total_w, height=total_h)

    # ------------------------------------------------------------------
    # Validation + per-cell helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _cell_str(value: Any) -> str:
        """Stringify a cell value.

        Floats render with 6 trailing-zero-trimmed decimal places by
        default; integers stay as integers; everything else routes
        through ``str()``. Authors who want bespoke formatting (e.g.
        ``"1.41421"``, ``"3/4"``) can pre-format strings before
        passing them in.
        """
        if isinstance(value, bool):
            return str(value)
        if isinstance(value, float):
            s = f"{value:.6f}"
            if "." in s:
                s = s.rstrip("0").rstrip(".")
            return s or "0"
        return str(value)

    def _validate_shape(self) -> None:
        n_cols = len(self.headers)
        for i, row in enumerate(self.rows):
            if len(row) != n_cols:
                raise ValueError(
                    f"row {i}: expected {n_cols} cells, got {len(row)}"
                )

    def _col_is_numeric(self, col: int) -> bool:
        """Heuristic: column is numeric if every non-empty cell parses as a number."""
        any_nonempty = False
        for row in self.rows:
            v = row[col].strip()
            if not v:
                continue
            any_nonempty = True
            try:
                float(v.replace(",", ""))
            except (ValueError, TypeError):
                return False
        return any_nonempty

    def _auto_col_widths(self, total_width: int) -> List[int]:
        """Distribute ``total_width`` across columns proportionally to content length.

        Each column gets at least the header width + padding. Excess
        budget gets shared so wider-content columns expand more.
        """
        n_cols = len(self.headers)
        if n_cols == 0:
            return []

        # Approximate text width: 8 px/char for serif, 9 for monospace
        # (numeric). Plus 2× padding.
        def col_min(i: int) -> int:
            char_w = 9 if self._col_is_numeric(i) else 8
            longest = max(
                [len(self.headers[i])]
                + [len(row[i]) for row in self.rows],
                default=0,
            )
            return longest * char_w + 2 * self._CELL_PADDING_X

        mins = [col_min(i) for i in range(n_cols)]
        sum_min = sum(mins)
        if sum_min >= total_width:
            return mins
        # Pad each column proportionally to mop up the remainder.
        leftover = total_width - sum_min
        per = leftover // n_cols
        return [m + per for m in mins]

    def _col_x(self, col: int) -> int:
        """Left edge x of column ``col``."""
        return sum(self.col_widths[:col])

    def _table_top(self) -> int:
        return self._CAPTION_HEIGHT if self.caption else 0

    # ------------------------------------------------------------------
    # to_svg
    # ------------------------------------------------------------------

    def to_svg(self) -> str:
        parts: List[str] = []

        if self.caption:
            cap_y = self._CAPTION_HEIGHT - 8
            cx = self.width / 2
            parts.append(
                f'<text x="{_fmt(cx)}" y="{_fmt(cap_y)}" '
                f'text-anchor="middle" font-family="Times New Roman, '
                f'Times, serif" font-size="14" font-style="italic">'
                f'{_esc(self.caption)}</text>'
            )

        top = self._table_top()
        # Header row background
        parts.append(
            f'<rect x="0" y="{_fmt(top)}" width="{self.width}" '
            f'height="{self._HEADER_HEIGHT}" fill="{self._HEADER_FILL}" '
            f'stroke="{self._GRID_STROKE}" stroke-width="1"/>'
        )

        # Highlight cells (under the grid lines so strokes still show)
        for r, c in self.highlights:
            if not (0 <= r < len(self.rows) and 0 <= c < len(self.headers)):
                continue
            cx = self._col_x(c)
            cy = top + self._HEADER_HEIGHT + r * self._ROW_HEIGHT
            parts.append(
                f'<rect x="{_fmt(cx)}" y="{_fmt(cy)}" '
                f'width="{self.col_widths[c]}" height="{self._ROW_HEIGHT}" '
                f'fill="{self._HIGHLIGHT_FILL}"/>'
            )

        # Header text
        for i, h in enumerate(self.headers):
            parts.append(self._cell_text(
                self.headers[i], i, -1, top, header=True,
            ))

        # Data rows
        for r, row in enumerate(self.rows):
            for c, cell in enumerate(row):
                parts.append(self._cell_text(cell, c, r, top))

        # Vertical grid lines (column boundaries)
        x = 0
        for w in self.col_widths:
            x += w
            parts.append(
                f'<line x1="{_fmt(x)}" y1="{_fmt(top)}" '
                f'x2="{_fmt(x)}" y2="{_fmt(top + self._HEADER_HEIGHT + len(self.rows) * self._ROW_HEIGHT)}" '
                f'stroke="{self._GRID_STROKE}" stroke-width="1"/>'
            )

        # Horizontal grid lines: under header + between every row
        y = top + self._HEADER_HEIGHT
        parts.append(
            f'<line x1="0" y1="{_fmt(y)}" x2="{self.width}" '
            f'y2="{_fmt(y)}" stroke="{self._GRID_STROKE}" stroke-width="1"/>'
        )
        for r in range(len(self.rows)):
            y += self._ROW_HEIGHT
            parts.append(
                f'<line x1="0" y1="{_fmt(y)}" x2="{self.width}" '
                f'y2="{_fmt(y)}" stroke="{self._GRID_STROKE}" stroke-width="1"/>'
            )

        # Outer bounding rect (covers the bottom line + ensures the
        # left edge stroke is present even if col_widths sum is 0).
        parts.append(
            f'<rect x="0" y="{_fmt(top)}" width="{self.width}" '
            f'height="{self._HEADER_HEIGHT + len(self.rows) * self._ROW_HEIGHT}" '
            f'fill="none" stroke="{self._GRID_STROKE}" stroke-width="1"/>'
        )

        return self._wrap(*parts)

    def _cell_text(
        self, text: str, col: int, row: int, top: int, *, header: bool = False,
    ) -> str:
        """Emit one cell's `<text>` element with the right alignment + font."""
        align = self.align[col]
        x_left = self._col_x(col)
        cell_w = self.col_widths[col]
        if align == "left":
            x = x_left + self._CELL_PADDING_X
            anchor = "start"
        elif align == "right":
            x = x_left + cell_w - self._CELL_PADDING_X
            anchor = "end"
        else:
            x = x_left + cell_w / 2
            anchor = "middle"

        if header:
            y = top + self._HEADER_HEIGHT - 11
            font_attrs = (
                'font-family="Times New Roman, Times, serif" '
                'font-size="14" font-weight="bold"'
            )
        else:
            y = top + self._HEADER_HEIGHT + row * self._ROW_HEIGHT \
                + self._ROW_HEIGHT - 9
            if self._col_is_numeric(col):
                font_attrs = (
                    'font-family="Courier New, Courier, monospace" '
                    'font-size="14"'
                )
            else:
                font_attrs = (
                    'font-family="Times New Roman, Times, serif" '
                    'font-size="14"'
                )

        return (
            f'<text x="{_fmt(x)}" y="{_fmt(y)}" text-anchor="{anchor}" '
            f'{font_attrs}>{_esc(text)}</text>'
        )

    # ------------------------------------------------------------------
    # to_text  (Unicode box-drawing)
    # ------------------------------------------------------------------

    def to_text(self) -> str:
        """ASCII / Unicode box-drawing rendering for terminals."""
        widths = [
            max(
                len(self.headers[c]),
                *(len(row[c]) for row in self.rows),
                1,
            )
            for c in range(len(self.headers))
        ]

        def fmt_cell(text: str, col: int) -> str:
            w = widths[col]
            if self.align[col] == "left":
                return text.ljust(w)
            if self.align[col] == "right":
                return text.rjust(w)
            return text.center(w)

        def horizontal(left: str, sep: str, right: str) -> str:
            segments = ["─" * (w + 2) for w in widths]
            return left + sep.join(segments) + right

        lines: List[str] = []
        if self.caption:
            lines.append(self.caption)
        lines.append(horizontal("┌", "┬", "┐"))
        lines.append(
            "│ " + " │ ".join(fmt_cell(h, i) for i, h in enumerate(self.headers)) + " │"
        )
        lines.append(horizontal("├", "┼", "┤"))
        for row in self.rows:
            lines.append(
                "│ " + " │ ".join(fmt_cell(c, i) for i, c in enumerate(row)) + " │"
            )
        lines.append(horizontal("└", "┴", "┘"))
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # to_markdown  (GFM pipe table)
    # ------------------------------------------------------------------

    def to_markdown(self) -> str:
        align_token = {
            "left": ":---",
            "right": "---:",
            "center": ":---:",
        }
        lines: List[str] = []
        if self.caption:
            lines.append(f"*{_md_escape(self.caption)}*")
            lines.append("")
        lines.append("| " + " | ".join(_md_escape(h) for h in self.headers) + " |")
        lines.append("| " + " | ".join(align_token[a] for a in self.align) + " |")
        for row in self.rows:
            lines.append(
                "| " + " | ".join(_md_escape(c) for c in row) + " |"
            )
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # to_latex  (tabular env)
    # ------------------------------------------------------------------

    def to_latex(self) -> str:
        align_letter = {"left": "l", "center": "c", "right": "r"}
        col_spec = "|" + "|".join(align_letter[a] for a in self.align) + "|"
        lines: List[str] = []
        if self.caption:
            lines.append(r"\begin{table}[h]")
            lines.append(r"\centering")
            lines.append(rf"\caption*{{{_latex_escape(self.caption)}}}")
        lines.append(rf"\begin{{tabular}}{{{col_spec}}}")
        lines.append(r"\hline")
        lines.append(
            " & ".join(rf"\textbf{{{_latex_escape(h)}}}" for h in self.headers)
            + r" \\"
        )
        lines.append(r"\hline")
        for row in self.rows:
            lines.append(" & ".join(_latex_escape(c) for c in row) + r" \\")
        lines.append(r"\hline")
        lines.append(r"\end{tabular}")
        if self.caption:
            lines.append(r"\end{table}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # render() default — keeps the visual-sandbox `Visual = ...` contract
    # ------------------------------------------------------------------

    def render(self) -> str:
        return self.to_svg()


# ---------------------------------------------------------------------------
# Variant subclasses — thin sugar over the base constructor.
# ---------------------------------------------------------------------------

class FunctionValueTable(TableSVG):
    """Two-column ``x | f(x)`` table for Riemann sums / derivative checks.

    Constructor takes parallel x / y sequences plus optional axis
    labels. When the caller passes a ``highlight_indices`` list, those
    rows get the standard highlight tint — useful for drawing the
    reader's eye to the rectangles a Riemann sum is summing over.
    """

    def __init__(
        self,
        x_values: Sequence[Any],
        y_values: Sequence[Any],
        *,
        x_label: str = "x",
        y_label: str = "f(x)",
        caption: Optional[str] = None,
        highlight_indices: Optional[Sequence[int]] = None,
        width: int = 320,
    ):
        if len(x_values) != len(y_values):
            raise ValueError(
                f"x_values ({len(x_values)}) and y_values ({len(y_values)}) "
                f"must have the same length"
            )
        rows = list(zip(x_values, y_values))
        # highlight_indices targets column 1 (the f(x) column) by
        # convention — that's the value the reader is checking.
        highlights = [(r, 1) for r in (highlight_indices or [])]
        super().__init__(
            headers=[x_label, y_label],
            rows=rows,
            caption=caption,
            highlights=highlights,
            width=width,
        )


class MatrixTable(TableSVG):
    """Matrix display.

    Sympy / numpy matrices supported via duck-typing on ``.tolist()``.
    Optional ``row_labels`` / ``col_labels`` add an extra labelled row
    or column for eigenvalue-problem displays.
    """

    def __init__(
        self,
        matrix,
        *,
        row_labels: Optional[Sequence[str]] = None,
        col_labels: Optional[Sequence[str]] = None,
        caption: Optional[str] = None,
        width: int = 320,
    ):
        if hasattr(matrix, "tolist"):
            data = matrix.tolist()
        else:
            data = [list(row) for row in matrix]
        if not data:
            raise ValueError("MatrixTable requires at least one row")

        n_cols = len(data[0])
        for i, row in enumerate(data):
            if len(row) != n_cols:
                raise ValueError(
                    f"row {i}: expected {n_cols} cells, got {len(row)}"
                )

        if col_labels is not None and len(col_labels) != n_cols:
            raise ValueError(
                f"col_labels: expected {n_cols} entries, got {len(col_labels)}"
            )
        if row_labels is not None and len(row_labels) != len(data):
            raise ValueError(
                f"row_labels: expected {len(data)} entries, got {len(row_labels)}"
            )

        # Headers: empty corner + col labels (or just blanks when col_labels=None).
        if col_labels is not None:
            headers = ([""] if row_labels is not None else []) + list(col_labels)
        else:
            headers = ([""] if row_labels is not None else []) + [""] * n_cols

        rows: List[List[Any]] = []
        for i, row in enumerate(data):
            if row_labels is not None:
                rows.append([row_labels[i]] + list(row))
            else:
                rows.append(list(row))

        super().__init__(
            headers=headers,
            rows=rows,
            caption=caption,
            width=width,
            align=["center"] * len(headers),
        )


class DataTable(TableSVG):
    """General-purpose data table — public alias for :class:`TableSVG`.

    Authors reaching for "I have rows of mixed-type data, lay it out
    as a table" should use this name; the explicit semantics make the
    YAML easier to skim. Behaviour is identical to ``TableSVG``.
    """
    pass


# ---------------------------------------------------------------------------
# Format-specific text helpers (markdown / latex escape)
# ---------------------------------------------------------------------------

def _md_escape(text: str) -> str:
    """Escape pipe characters that would break GFM table cells."""
    return str(text).replace("|", r"\|")


