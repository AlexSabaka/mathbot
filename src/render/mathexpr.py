"""B.5 keystone: single internal representation of math content.

Every Phase γ rendering pipeline (text, markdown, latex, pdf, svg, png)
routes math through ``MathExpr`` so the same sympy expression typesets
consistently across all six output forms. Without this centralisation
the four math-bearing renderers drift, and "x squared plus one" ends
up as ``x**2 + 1`` in the markdown row, ``x^2 + 1`` in the latex row,
and ``x² + 1`` in the text row — same problem, three different
canonical forms.

Today:

- :meth:`MathExpr.to_text` — single-line Unicode (``x²``, ``≤``, ``∫``,
  ``→``). Routes through :func:`sympy.pretty` with ``num_columns`` set
  high enough to flatten fractions onto one line.
- :meth:`MathExpr.to_markdown` — GitHub-Flavored Markdown / GH MathJax:
  the LaTeX form wrapped in ``$...$``. ``$$...$$`` block form is
  authored explicitly when the surrounding context calls for it; the
  default is inline.
- :meth:`MathExpr.to_latex` — raw LaTeX (no ``$`` delimiters), suitable
  for direct interpolation into a tex document.

Deferred to Phase γ.2 / γ.3:

- :meth:`MathExpr.to_svg` — KaTeX → SVG. Stubbed as
  :exc:`NotImplementedError` until a KaTeX strategy is decided
  (vendored ``katex-cli`` subprocess vs. ``katex`` PyPI wrapper).
- :meth:`MathExpr.to_png` — KaTeX → SVG → cairosvg raster. Same
  blocker.

The constructor accepts the value forms a Phase α / β solution
sandbox actually produces: ``sympy.Expr``, ``sympy.Matrix``, Python
``int`` / ``float`` / ``complex``, free-form strings (parsed via
``sympy.sympify``; passthrough on parse failure). Anything else
falls through to ``str(value)`` in every renderer — a deliberate
softness so the keystone never breaks a pipeline at the renderer
layer.
"""

from __future__ import annotations

import re
from typing import Any

import sympy as sp
from sympy.parsing.sympy_parser import parse_expr as _parse_expr


_SUP_DIGITS = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
_SUB_DIGITS = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
_POW_RE = re.compile(r"\*\*\(?(-?\d+)\)?")


def _to_unicode_inline(text: str) -> str:
    """Lift ``sympy.sstr`` output to single-line Unicode.

    ``sp.pretty`` emits a 2-D glyph layout that doesn't survive the
    one-line collapse the keystone needs (``x**2`` becomes
    ``" 2 \\nx  + 1"`` which flattens to ``"2 x + 1"``), so we work
    from ``sp.sstr`` (Python form: ``x**2 + 1``) and apply targeted
    substitutions:

    - ``**N`` and ``**(-N)`` → Unicode superscript digits (``x²``,
      ``x⁻¹``).
    - ``oo`` → ``∞`` (sympy's stand-in for infinity).
    - ``Eq(a, b)``, ``a <= b``, ``a >= b``, ``a != b`` → ``a = b``,
      ``a ≤ b``, ``a ≥ b``, ``a ≠ b``.

    Conservative on purpose: we don't try to lift ``*`` to implicit
    juxtaposition (``2*x`` → ``2x``) because greek-letter constants
    like ``pi*x`` would mangle to ``pix``. ``2*x + 1`` stays
    ``2*x + 1`` until a pipeline-specific text renderer wants to
    refine it.
    """
    def _pow_repl(match: re.Match) -> str:
        n = match.group(1)
        if n.startswith("-"):
            return "⁻" + n[1:].translate(_SUP_DIGITS)
        return n.translate(_SUP_DIGITS)

    text = _POW_RE.sub(_pow_repl, text)
    text = text.replace("<=", "≤").replace(">=", "≥").replace("!=", "≠")
    text = re.sub(r"\boo\b", "∞", text)
    return text


class MathExpr:
    """Math content with multi-target rendering."""

    __slots__ = ("_raw", "_sympy")

    def __init__(self, value: Any):
        self._raw = value
        self._sympy = self._coerce(value)

    @staticmethod
    def _coerce(value: Any) -> Any:
        """Normalise to a sympy object where possible.

        Returns the parsed sympy expression / matrix, or ``None`` if
        ``value`` doesn't round-trip through ``sympify``. The
        per-renderer fallback then uses ``str(self._raw)``.
        """
        if isinstance(value, sp.Basic) or isinstance(value, sp.MatrixBase):
            return value
        if isinstance(value, bool):
            # bool is a subclass of int — distinguish before the int branch
            # so True/False render as Python literals, not as 1/0.
            return None
        if isinstance(value, (int, float)):
            return sp.Number(value)
        if isinstance(value, complex):
            # Build an exact a + b*I expression; sp.sympify on a complex
            # literal goes through Python's repr which is fine but loses
            # exactness for tiny imaginary residuals from float arithmetic.
            return sp.Add(
                sp.Number(value.real),
                sp.Mul(sp.Number(value.imag), sp.I),
            )
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return None
            # parse_expr(evaluate=False) preserves the algebraic form a
            # template author wrote: ``2*(t + 1)*exp(-t)`` round-trips
            # to ``2*(t + 1)*exp(-t)`` rather than the auto-distributed
            # ``(2*t + 2)*exp(-t)`` that ``sp.sympify`` would produce.
            # Critical for cross-format consistency — the SVG-composite
            # path uses the formatter's plain-string answer, so the
            # markdown/latex paths must preserve the same form when
            # they typeset it.
            try:
                return _parse_expr(stripped, evaluate=False)
            except (SyntaxError, TypeError, ValueError, AttributeError, sp.SympifyError):
                # parse_expr is stricter than sympify — fall back to
                # sympify on parse failure (handles older sympy syntax,
                # custom symbols, etc.). The eager evaluation here is
                # acceptable as a fallback because the round-trip
                # already failed the strict path.
                try:
                    return sp.sympify(stripped)
                except (sp.SympifyError, SyntaxError, TypeError, ValueError):
                    return None
        return None

    # ------------------------------------------------------------------
    # Renderers
    # ------------------------------------------------------------------

    def to_text(self) -> str:
        """Single-line Unicode rendering.

        Matrices: bracket form ``[[1, 2], [3, 4]]`` rather than the
        multi-line sympy pretty form, because text-mode output goes
        into prose where a one-liner reads cleanly. LaTeX-mode and
        markdown-mode get the proper layout.

        Expressions: ``sp.sstr`` Python form lifted to Unicode via
        :func:`_to_unicode_inline` (``x²`` instead of ``x**2``,
        ``∞`` instead of ``oo``, ``≤`` instead of ``<=``).
        ``sp.pretty`` is *not* used here because its 2-D layout
        ("``2 / x + 1``" with the ``2`` on its own line) doesn't
        survive the one-line collapse the keystone needs.
        """
        if isinstance(self._sympy, sp.MatrixBase):
            rows = [
                "[" + ", ".join(self._unicode_atom(c) for c in row) + "]"
                for row in self._sympy.tolist()
            ]
            return "[" + ", ".join(rows) + "]"
        if self._sympy is not None:
            # sympy's sstr renders Eq as the function-call form
            # ``Eq(lhs, rhs)`` rather than ``lhs = rhs``. The relational
            # output a K12 problem author wants is the infix form, so
            # special-case it and let the lhs/rhs go through the same
            # Unicode lift as any other expression.
            if isinstance(self._sympy, sp.Equality):
                lhs = _to_unicode_inline(sp.sstr(self._sympy.lhs))
                rhs = _to_unicode_inline(sp.sstr(self._sympy.rhs))
                return f"{lhs} = {rhs}"
            try:
                rendered = sp.sstr(self._sympy)
            except Exception:
                return str(self._raw)
            return _to_unicode_inline(rendered)
        return str(self._raw)

    def to_latex(self) -> str:
        """Raw LaTeX (no ``$`` delimiters)."""
        if self._sympy is not None:
            return sp.latex(self._sympy)
        return str(self._raw)

    def to_markdown(self) -> str:
        """GH MathJax: ``$<latex>$`` (inline math).

        Block form (``$$...$$``) is the caller's responsibility — wrap
        ``to_latex()`` in ``$$ ... $$`` directly when a display block
        is wanted. The default inline form is what the prose renderer
        wants for variable substitutions inside problem text.
        """
        return f"${self.to_latex()}$"

    def to_svg(self) -> str:
        """KaTeX-rendered SVG. Deferred to γ.2/γ.3."""
        raise NotImplementedError(
            "MathExpr.to_svg requires KaTeX integration (deferred to γ.2/γ.3); "
            "use to_latex() and a separate KaTeX runner in the meantime."
        )

    def to_png(self) -> bytes:
        """KaTeX → SVG → raster. Deferred to γ.2/γ.3."""
        raise NotImplementedError(
            "MathExpr.to_png requires KaTeX integration (deferred to γ.2/γ.3); "
            "use to_latex() and a separate KaTeX runner in the meantime."
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _unicode_atom(value: Any) -> str:
        """Render a single matrix cell as a one-line Unicode string."""
        if isinstance(value, sp.Basic):
            try:
                return _to_unicode_inline(sp.sstr(value))
            except Exception:
                return sp.sstr(value)
        return str(value)

    # ------------------------------------------------------------------
    # Dunder protocol
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return f"MathExpr({self._raw!r})"

    def __str__(self) -> str:
        return self.to_text()

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, MathExpr):
            return NotImplemented
        # Equality on the underlying sympy object when both parse;
        # otherwise fall back to raw equality. This is permissive on
        # purpose — MathExpr is a wrapper, not an algebraic type.
        if self._sympy is not None and other._sympy is not None:
            try:
                return bool(sp.simplify(self._sympy - other._sympy) == 0)
            except Exception:
                pass
        return self._raw == other._raw
