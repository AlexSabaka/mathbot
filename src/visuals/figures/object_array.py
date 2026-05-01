"""γ.4s — :class:`ObjectArray`: K1 row-of-items workhorse.

Renders the canonical K1 visualisations: N copies of an item-glyph
laid out in a row. Three modes layer on top of the base row:

- **Plain count**: ``count=5`` → five circles in a row (counting,
  ten-frame fragments, "how many?" prompts).
- **Grouped**: ``groups=[5, 3]`` inserts a wider gap between the two
  sub-rows, visualising "5 + 3 = ?" without subtotaling glyphs.
- **Strikes**: ``strikes=[5, 6, 7]`` overlays a red X across the named
  positions, visualising "8 - 3 = ?" by crossing out three of eight.
- **Comparison**: ``comparison=(8, 5)`` overrides everything else and
  draws *two* parallel rows, top with 8 items, bottom with 5, for
  side-by-side counting / "which has more?" prompts.

Item rendering routes through :func:`shape_glyph.glyph_for` so the
prose-item name in the template (``"apples"``, ``"books"``,
``"stars"``…) maps to a deterministic geometric primitive. Unknown
items fall back to ``circle`` — never raises.

Multi-format rendering follows the γ.3 contract every figure builder
shares:

- :meth:`to_svg` — self-contained SVG (also returned by :meth:`render`).
- :meth:`to_text` — one-paragraph ASCII description.
- :meth:`to_latex` — TikZ for plain rows / groups / strikes; an
  ``\\fbox{[Figure: ...]}`` fallback for the comparison mode where
  the layout combinatorics outweigh the value of bespoke TikZ.

Determinism: same constructor args → byte-identical SVG.
"""

from __future__ import annotations

from typing import Callable, List, Optional, Tuple

from ..base import DEFAULT_FONT, SVGBuilder, _esc, _fmt, _latex_escape
from .shape_glyph import glyph_for


# Strike colour / stroke width — the standard "red X" of K1 worksheets.
_STRIKE_COLOR = "#dc2626"
_STRIKE_WIDTH = 3
# Group-gap multiplier: a group break is 1.5× a normal item-to-item
# spacing. Wide enough to read as "two groups", narrow enough that the
# whole row still fits the viewport for typical counts (≤12).
_GROUP_GAP_MULT = 1.5
# Auto-bumped minimum height for comparison mode (two rows + breathing
# room).
_COMPARISON_MIN_HEIGHT = 160


class ObjectArray(SVGBuilder):
    """Row(s) of countable item-glyphs with optional groupings, strikes, comparison.

    Parameters
    ----------
    count:
        Total number of items in the row. Ignored when ``comparison``
        is set.
    item:
        Prose item name (``"apples"``, ``"books"``, ``"dots"``, …),
        routed through :func:`glyph_for` to pick the glyph primitive.
        Unknown names fall back to ``circle``.
    groups:
        If set, a list of integers summing to ``count``. A wider gap
        is inserted between groups (``1.5×`` normal item spacing) so
        the row reads as "5 + 3 = ?" rather than "8 in a line".
    strikes:
        If set, the 0-indexed positions of items that should be
        crossed out with a red X. Out-of-range indices are silently
        ignored so a slightly-off ``strikes`` list never breaks the
        render.
    comparison:
        If set, a ``(top_count, bottom_count)`` tuple. Overrides
        ``count`` / ``groups`` / ``strikes`` and draws two parallel
        rows. Auto-bumps ``height`` to at least
        ``_COMPARISON_MIN_HEIGHT`` so both rows fit.
    glyph_size:
        Bounding-box size for each glyph in SVG units.
    glyph_fill:
        Fill colour passed to the glyph function.
    width, height:
        SVG viewport dimensions. ``height`` is auto-bumped when
        ``comparison`` is active.
    """

    def __init__(
        self,
        count: int = 5,
        item: str = "dots",
        groups: Optional[List[int]] = None,
        strikes: Optional[List[int]] = None,
        comparison: Optional[Tuple[int, int]] = None,
        glyph_size: float = 24,
        glyph_fill: str = "#fb923c",
        width: int = 480,
        height: int = 80,
    ):
        # Auto-bump height for comparison mode *before* calling super so
        # the SVG envelope reports the bumped height to renderers.
        if comparison is not None and height < _COMPARISON_MIN_HEIGHT:
            height = _COMPARISON_MIN_HEIGHT
        super().__init__(width=width, height=height)

        if count < 0:
            raise ValueError(f"count must be >= 0, got {count}")
        if glyph_size <= 0:
            raise ValueError(f"glyph_size must be > 0, got {glyph_size}")

        self.count = int(count)
        self.item = str(item)
        self.glyph_size = float(glyph_size)
        self.glyph_fill = str(glyph_fill)

        # Validate groups: must sum to count when supplied. Reject
        # negative entries — they'd produce a backward-running layout.
        if groups is not None:
            groups = [int(g) for g in groups]
            if any(g < 0 for g in groups):
                raise ValueError(
                    f"groups entries must be >= 0, got {groups}"
                )
            if sum(groups) != self.count:
                raise ValueError(
                    f"groups must sum to count ({self.count}), "
                    f"got {groups} (sum={sum(groups)})"
                )
        self.groups: Optional[List[int]] = groups

        # Strikes: store as a frozenset of valid indices for O(1) lookup
        # during render. Out-of-range entries are silently dropped so a
        # mildly-off ``strikes`` list never breaks the render.
        if strikes is not None:
            self._strike_set = frozenset(
                i for i in (int(s) for s in strikes)
                if 0 <= i < self.count
            )
        else:
            self._strike_set = frozenset()
        # Keep the raw list around for to_text() reporting (preserves the
        # author's intent even when an entry is out-of-range).
        self.strikes: Optional[List[int]] = (
            [int(s) for s in strikes] if strikes is not None else None
        )

        if comparison is not None:
            top, bottom = comparison
            top, bottom = int(top), int(bottom)
            if top < 0 or bottom < 0:
                raise ValueError(
                    f"comparison counts must be >= 0, got {comparison}"
                )
            self.comparison: Optional[Tuple[int, int]] = (top, bottom)
        else:
            self.comparison = None

        # Resolve glyph once — :func:`glyph_for` is cheap, but caching
        # the lookup keeps render() pure-arithmetic.
        self._glyph: Callable[..., str] = glyph_for(self.item)

    # ------------------------------------------------------------------
    # Geometry helpers
    # ------------------------------------------------------------------

    def _row_positions(self, n: int) -> List[float]:
        """Return the x-centres for ``n`` items spaced evenly across the row.

        Items are inset from the viewport edges by half a glyph plus a
        small margin so the leftmost/rightmost glyph doesn't clip the
        viewBox. For ``n == 0`` returns an empty list. For ``n == 1``
        returns the single midpoint.
        """
        if n <= 0:
            return []
        margin = self.glyph_size * 0.75
        usable = max(self.width - 2 * margin, 0.0)
        if n == 1:
            return [self.width / 2]
        step = usable / (n - 1)
        return [margin + i * step for i in range(n)]

    def _grouped_positions(self) -> List[float]:
        """Like :meth:`_row_positions` but with widened gaps at group breaks.

        We compute the *unit count*: each item contributes 1 unit of
        spacing to its right neighbour, except at group boundaries
        where the contribution is ``_GROUP_GAP_MULT``. Then we divide
        the available width by total units to get a per-unit step.
        """
        if not self.groups or self.count <= 0:
            return self._row_positions(self.count)
        if self.count == 1:
            return [self.width / 2]

        # Build a flat list of "is this position the *first* of a new
        # group (after the first)?" — those breaks consume more space.
        breaks: List[bool] = []
        running = 0
        for gi, g in enumerate(self.groups):
            for j in range(g):
                # First item of every group except the very first one
                # is a "break" position.
                breaks.append(gi > 0 and j == 0)
            running += g

        # Total spacing units between adjacent items: regular gap = 1.0,
        # group break gap = _GROUP_GAP_MULT.
        unit_total = 0.0
        for i in range(1, self.count):
            unit_total += _GROUP_GAP_MULT if breaks[i] else 1.0

        margin = self.glyph_size * 0.75
        usable = max(self.width - 2 * margin, 0.0)
        step = usable / unit_total if unit_total > 0 else 0.0

        positions = [margin]
        for i in range(1, self.count):
            gap = _GROUP_GAP_MULT if breaks[i] else 1.0
            positions.append(positions[-1] + step * gap)
        return positions

    def _strike_snippet(self, cx: float, cy: float) -> str:
        """Two-line red X across the glyph bounding box at ``(cx, cy)``."""
        half = self.glyph_size / 2
        x1 = cx - half
        y1 = cy - half
        x2 = cx + half
        y2 = cy + half
        return (
            f'<line x1="{_fmt(x1)}" y1="{_fmt(y1)}" '
            f'x2="{_fmt(x2)}" y2="{_fmt(y2)}" '
            f'stroke="{_STRIKE_COLOR}" stroke-width="{_STRIKE_WIDTH}" '
            f'stroke-linecap="round"/>'
            f'<line x1="{_fmt(x1)}" y1="{_fmt(y2)}" '
            f'x2="{_fmt(x2)}" y2="{_fmt(y1)}" '
            f'stroke="{_STRIKE_COLOR}" stroke-width="{_STRIKE_WIDTH}" '
            f'stroke-linecap="round"/>'
        )

    # ------------------------------------------------------------------
    # to_svg
    # ------------------------------------------------------------------

    def to_svg(self) -> str:
        if self.comparison is not None:
            return self._render_comparison()
        return self._render_row()

    def _render_row(self) -> str:
        """Single-row mode: optional groups + optional strikes."""
        cy = self.height / 2
        positions = (
            self._grouped_positions()
            if self.groups
            else self._row_positions(self.count)
        )
        parts: List[str] = []
        for i, cx in enumerate(positions):
            parts.append(
                self._glyph(cx, cy, self.glyph_size, self.glyph_fill)
            )
            if i in self._strike_set:
                parts.append(self._strike_snippet(cx, cy))
        return self._wrap(*parts)

    def _render_comparison(self) -> str:
        """Two-row comparison mode.

        Top row centred at ``height/3``, bottom row at ``2*height/3``.
        Strikes / groups are intentionally ignored here — comparison is
        a different layout intent, and surfacing strikes would clash
        with the "which has more?" framing.
        """
        assert self.comparison is not None
        top_n, bottom_n = self.comparison
        y_top = self.height / 3
        y_bottom = 2 * self.height / 3

        parts: List[str] = []
        for cx in self._row_positions_for(top_n):
            parts.append(
                self._glyph(cx, y_top, self.glyph_size, self.glyph_fill)
            )
        for cx in self._row_positions_for(bottom_n):
            parts.append(
                self._glyph(cx, y_bottom, self.glyph_size, self.glyph_fill)
            )
        return self._wrap(*parts)

    def _row_positions_for(self, n: int) -> List[float]:
        """Convenience for comparison mode: un-grouped row positions for ``n`` items.

        Comparison mode never groups (visual intent is "two rows side
        by side"), so this just delegates to :meth:`_row_positions`.
        """
        return self._row_positions(n)

    # ------------------------------------------------------------------
    # to_text
    # ------------------------------------------------------------------

    def to_text(self) -> str:
        """One-sentence ASCII description.

        Phrasing branches on mode so screen-readers and alt-text
        consumers get a faithful description of *what's drawn*, not
        just the parameters.
        """
        item = self.item
        if self.comparison is not None:
            top, bottom = self.comparison
            return (
                f"Comparison: top row of {top} {item}; "
                f"bottom row of {bottom} {item}."
            )

        # Single-row branches.
        if self.count == 0:
            return f"Empty row (no {item})."

        # Strike phrasing only kicks in when at least one valid strike
        # actually lands on an item.
        if self._strike_set:
            n_strikes = len(self._strike_set)
            # If the strikes are exactly the trailing items, the prose
            # reads more naturally as "the last N are crossed out".
            tail = set(range(self.count - n_strikes, self.count))
            if self._strike_set == tail and n_strikes > 0:
                strike_phrase = (
                    f"; the last {n_strikes} are crossed out"
                    if n_strikes > 1
                    else "; the last one is crossed out"
                )
            else:
                strike_phrase = (
                    f"; {n_strikes} are crossed out"
                    if n_strikes > 1
                    else "; one is crossed out"
                )
        else:
            strike_phrase = ""

        if self.groups and len(self.groups) >= 2:
            # "Row of 5 apples grouped with 3 more apples." for two
            # groups; a generic listing for three or more.
            if len(self.groups) == 2:
                a, b = self.groups
                base = (
                    f"Row of {a} {item} grouped with {b} more {item}"
                )
            else:
                joined = ", ".join(str(g) for g in self.groups)
                base = f"Row of {item} in groups of {joined}"
        else:
            base = f"Row of {self.count} {item}"

        return base + strike_phrase + "."

    # ------------------------------------------------------------------
    # to_latex
    # ------------------------------------------------------------------

    def to_latex(self) -> str:
        """TikZ rendering for row mode; ``\\fbox`` fallback for comparison.

        Per the γ.3 contract we ship real TikZ wherever the geometry
        is straightforward. Comparison mode (two rows + per-row glyph
        layouts) is a clean candidate for the ``\\fbox`` fallback —
        the visual is fine in SVG, and the LaTeX consumer mostly wants
        a placeholder describing what would render.
        """
        if self.comparison is not None:
            top, bottom = self.comparison
            return (
                rf"\fbox{{[Figure: comparison of {top} vs {bottom} "
                rf"{_latex_escape(self.item)}]}}"
            )

        lines: List[str] = [r"\begin{tikzpicture}"]

        # Pick the TikZ primitive that mirrors the SVG glyph. The
        # mapping is intentionally small — it covers the prose items
        # the K1 corpus uses today; unknowns fall back to a circle to
        # match :func:`glyph_for`.
        tikz_kind = self._glyph_tikz_kind()

        positions = (
            self._grouped_positions()
            if self.groups
            else self._row_positions(self.count)
        )
        # Convert SVG-pixel positions into TikZ centimetres so the
        # output fits a typical printed page. 20 SVG units ≈ 1 cm
        # matches the convention used in :class:`SectorFigure`.
        cy_cm = (self.height / 2) / 20.0
        size_cm = self.glyph_size / 20.0

        for i, cx_px in enumerate(positions):
            cx_cm = cx_px / 20.0
            lines.append(self._tikz_glyph(tikz_kind, cx_cm, cy_cm, size_cm))
            if i in self._strike_set:
                # Two diagonal red strokes form the X. ``red`` is TikZ's
                # built-in name; thick stroke matches the SVG version.
                half = size_cm / 2
                lines.append(
                    rf"  \draw[red, thick] "
                    rf"({_fmt(cx_cm - half)},{_fmt(cy_cm - half)}) -- "
                    rf"({_fmt(cx_cm + half)},{_fmt(cy_cm + half)});"
                )
                lines.append(
                    rf"  \draw[red, thick] "
                    rf"({_fmt(cx_cm - half)},{_fmt(cy_cm + half)}) -- "
                    rf"({_fmt(cx_cm + half)},{_fmt(cy_cm - half)});"
                )

        lines.append(r"\end{tikzpicture}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # TikZ glyph mapping
    # ------------------------------------------------------------------

    def _glyph_tikz_kind(self) -> str:
        """Return the TikZ primitive name matching the current SVG glyph.

        Mirrors the dispatcher in :mod:`shape_glyph`; we re-derive
        rather than import a private map so the two modules can evolve
        independently. Unknown items fall back to ``"circle"`` to mirror
        :func:`glyph_for`'s circle-fallback contract.
        """
        from .shape_glyph import circle, dot, heart, rounded_rect, star, triangle

        glyph_to_kind = {
            circle: "circle",
            rounded_rect: "rounded_rect",
            triangle: "triangle",
            star: "star",
            heart: "heart",
            dot: "dot",
        }
        return glyph_to_kind.get(self._glyph, "circle")

    @staticmethod
    def _tikz_glyph(kind: str, cx: float, cy: float, size: float) -> str:
        """Emit a single TikZ ``\\draw`` line for the given primitive.

        The ``size`` here is the SVG bounding-box size in cm (already
        converted by the caller). Each branch reproduces the same
        proportions as :mod:`shape_glyph`.
        """
        cx_s, cy_s = _fmt(cx), _fmt(cy)
        if kind == "circle":
            r = _fmt(size / 2)
            return rf"  \draw[fill=orange!70] ({cx_s},{cy_s}) circle ({r});"
        if kind == "rounded_rect":
            # 1.2:1 aspect, matching shape_glyph.rounded_rect.
            w = size
            h = size * 0.83
            x1 = _fmt(cx - w / 2)
            y1 = _fmt(cy - h / 2)
            x2 = _fmt(cx + w / 2)
            y2 = _fmt(cy + h / 2)
            return (
                rf"  \draw[fill=blue!40, rounded corners=2pt] "
                rf"({x1},{y1}) rectangle ({x2},{y2});"
            )
        if kind == "triangle":
            half = size / 2
            h = size * 0.866
            return (
                rf"  \draw[fill=green!50] "
                rf"({_fmt(cx)},{_fmt(cy + h / 2)}) -- "
                rf"({_fmt(cx - half)},{_fmt(cy - h / 2)}) -- "
                rf"({_fmt(cx + half)},{_fmt(cy - h / 2)}) -- cycle;"
            )
        if kind == "star":
            # TikZ ships a star shape via the ``shapes.geometric`` lib,
            # but pulling that in just for this would be heavy. A
            # filled "5-pointed star" via the regular polygon decoration
            # would also need extra packages — fall back to a labelled
            # node-circle so the document still compiles standalone.
            r = _fmt(size / 2)
            return (
                rf"  \draw[fill=yellow!70] ({cx_s},{cy_s}) circle ({r}) "
                rf"node {{$\star$}};"
            )
        if kind == "heart":
            # No portable heart primitive without extra packages; use a
            # filled circle with a heart glyph node so output still
            # compiles cleanly with the bare ``tikz`` package.
            r = _fmt(size / 2)
            return (
                rf"  \draw[fill=pink!70] ({cx_s},{cy_s}) circle ({r}) "
                rf"node {{$\heartsuit$}};"
            )
        if kind == "dot":
            r = _fmt(size * 0.35 / 2)
            return rf"  \fill[black] ({cx_s},{cy_s}) circle ({r});"
        # Defensive fallback — shouldn't fire because _glyph_tikz_kind
        # already normalises unknown glyphs to "circle".
        r = _fmt(size / 2)
        return rf"  \draw ({cx_s},{cy_s}) circle ({r});"

    # ------------------------------------------------------------------
    # render() default — keeps the visual-sandbox `Visual = ...` contract
    # ------------------------------------------------------------------

    def render(self) -> str:
        return self.to_svg()
