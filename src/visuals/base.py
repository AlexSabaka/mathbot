"""Shared SVG-builder primitives for the Phase β Approach-B visuals.

Builders return self-contained `<svg>` strings — no external CSS, no
external fonts. Default text uses a serif fallback chain for
mathematical readability across renderers (browsers, cairosvg).

Authoring constraint: every builder's `render()` must be deterministic
in its inputs so the same template + seed produces a byte-identical
visual.source value (lint enforces fixture stability via the existing
fixture-drift check).
"""

from __future__ import annotations

from typing import List


SVG_NS = "http://www.w3.org/2000/svg"
DEFAULT_FONT = (
    'font-family="Times New Roman, Times, serif" font-size="14"'
)


def _esc(text: str) -> str:
    """Escape user-supplied label text for SVG.

    Handles `<`, `>`, `&`, `"`, `'`. Templates may pass mathematical
    notation (`P(A | B)`, `x²`, `θ`) and the SVG must round-trip them
    untouched as far as the renderer is concerned.
    """
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def _fmt(x: float, ndigits: int = 2) -> str:
    """Format a float for SVG coordinates without trailing zeros.

    SVG renderers accept floats but the visual.source should be lean
    so dataset bytes don't bloat. Strip trailing zeros and a dangling
    decimal point.
    """
    s = f"{x:.{ndigits}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s or "0"


_LATEX_ESCAPES = {
    "\\": r"\textbackslash{}",
    "{": r"\{",
    "}": r"\}",
    "$": r"\$",
    "&": r"\&",
    "#": r"\#",
    "%": r"\%",
    "_": r"\_",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def _latex_escape(text: str) -> str:
    """Escape user-supplied label text for LaTeX output.

    Builders ship `to_latex()` methods that interpolate author-supplied
    labels into TikZ scenes; LaTeX's reserved characters (``$``, ``&``,
    ``%``, ``_``, ``#``, ``{``, ``}``, ``\\``, ``^``, ``~``) need
    escaping or the document fails to compile. Mirrors
    ``src.render.latex._latex_escape``; centralised here so figure
    builders don't each copy the table.
    """
    text = str(text)
    if not any(c in text for c in _LATEX_ESCAPES):
        return text
    return "".join(_LATEX_ESCAPES.get(c, c) for c in text)


class SVGBuilder:
    """Base class. Subclasses override `render()` to emit SVG markup.

    Common helpers — viewport boilerplate and the standard escape /
    coordinate-format primitives — live here to keep individual
    builders short.
    """

    def __init__(self, width: int = 400, height: int = 300):
        self.width = int(width)
        self.height = int(height)

    def _open_svg(self) -> str:
        """Open `<svg>` with a viewBox sized to (width, height)."""
        return (
            f'<svg xmlns="{SVG_NS}" width="{self.width}" height="{self.height}" '
            f'viewBox="0 0 {self.width} {self.height}">'
        )

    def _close_svg(self) -> str:
        return "</svg>"

    def _wrap(self, *parts: str) -> str:
        return self._open_svg() + "".join(parts) + self._close_svg()

    def render(self) -> str:  # pragma: no cover — overridden
        raise NotImplementedError("SVGBuilder subclasses must implement render()")
