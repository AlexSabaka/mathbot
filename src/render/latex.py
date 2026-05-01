"""B.3 LaTeX-rendering pipeline.

Renders a generated problem dict as a LaTeX document (or fragment).
The full document mode targets `tectonic` compilation in :mod:`B.4`;
the fragment mode lets a downstream system splice the body into its
own document.

Preamble: ``article`` class with ``geometry``, ``amsmath``, ``amssymb``,
``graphicx``, ``siunitx``, and ``hyperref``. ``tikz`` is included
even though γ.2 doesn't yet emit TikZ — γ.3's ``FigureSVG.to_latex()``
will start producing it, so the preamble is forward-compatible.

Body-text escaping: LaTeX has ten reserved characters that need
backslash-escaping inside text mode (``& % $ # _ { } ~ ^ \\``).
Math content authored in problem prose ("the value 2*x+1") goes
through the same escape — it stays as plain text. Math markup
intended to typeset properly should be written by the template
author as ``\\(...\\)`` and will pass through untouched (we don't
escape inside the math delimiters).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Optional

# MathExpr retained for forward use; the answer-render path uses
# plain-string-with-LaTeX-escape today — see _format_answer_latex.
from .mathexpr import MathExpr  # noqa: F401


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def render_latex(
    problem: Dict,
    *,
    show_answer: bool = True,
    fragment: bool = False,
    image_path: Optional[Path] = None,
) -> str:
    """Render a generated problem dict as LaTeX.

    ``fragment=False`` (default) returns a complete document with
    preamble. ``fragment=True`` returns the body content only —
    suitable for `\\input{...}`-ing into another document.

    ``image_path`` is the path passed to ``\\includegraphics`` when
    a visual is present. The caller is responsible for writing the
    visual (PNG or SVG-converted-to-PDF) to that path before
    compiling. If ``None``, the visual is omitted with no placeholder.
    """
    body = _render_body(problem, show_answer=show_answer, image_path=image_path)
    if fragment:
        return body
    return _PREAMBLE + body + _DOCUMENT_TAIL


def latex_escape(text: str) -> str:
    """Escape LaTeX-reserved characters in plain prose.

    Public so the lint-rule `latex_escape_check` (γ.3) can call it
    on alt-text and test fixtures to detect raw special characters
    that would break a tectonic compile.
    """
    return _latex_escape(text)


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------

# Preamble chosen for "compiles under tectonic with no extra packages"
# rather than maximal feature coverage. siunitx covers unit suffixes
# (`\\si{\\meter}`, `\\SI{5}{\\kilo\\gram}`); amsmath/amssymb cover
# the typical K9–K12 algebraic notation. hyperref + graphicx are the
# usual companions. tikz is loaded even though γ.2 emits no TikZ
# directly so γ.3 builders can produce it without reshipping the
# preamble.
_PREAMBLE = r"""\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage{siunitx}
\usepackage{tikz}
\usepackage{hyperref}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0.5em}

\begin{document}

"""

_DOCUMENT_TAIL = r"""

\end{document}
"""

# Order matters: \\ must be substituted first (it's its own escape),
# otherwise the substitution for { would mangle it. The dict ordering
# here is the substitution order — Python 3.7+ dicts are insertion-
# ordered.
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
    """Escape LaTeX special characters in body prose.

    A small fast-path: if the string contains none of the special
    characters, return it unchanged (most K1–K8 problem text is
    plain ASCII letters + digits + spaces + ASCII punctuation that
    LaTeX accepts as-is).
    """
    if not text:
        return text
    if not any(c in text for c in _LATEX_ESCAPES):
        return text
    out_parts: list[str] = []
    for ch in text:
        out_parts.append(_LATEX_ESCAPES.get(ch, ch))
    return "".join(out_parts)


def _render_body(
    problem: Dict,
    *,
    show_answer: bool,
    image_path: Optional[Path],
) -> str:
    """Body content (no preamble, no document begin/end)."""
    raw_body = problem.get('problem', '').rstrip()
    body_tex = _escape_body(raw_body)

    chunks: list[str] = []
    chunks.append(r"\section*{Problem}")
    chunks.append("")
    chunks.append(body_tex)

    visual = problem.get('visual') or {}
    alt_text = visual.get('alt_text')
    if image_path is not None and visual.get('source'):
        # Caller has prepared an image; embed it. ``image_path`` may
        # be relative (resolved against the .tex working dir at
        # compile time) or absolute.
        chunks.append("")
        chunks.append(r"\begin{figure}[h]")
        chunks.append(r"\centering")
        chunks.append(
            r"\includegraphics[width=0.7\textwidth]{" + str(image_path) + "}"
        )
        if alt_text:
            chunks.append(r"\caption*{" + _latex_escape(str(alt_text)) + "}")
        chunks.append(r"\end{figure}")

    if show_answer:
        answer_str = problem.get('task_params', {}).get('expected_answer', '')
        chunks.append("")
        chunks.append(r"\textbf{Answer:} " + _format_answer_latex(answer_str))

    return "\n".join(chunks)


# Pattern: skip content inside \(...\) or \[...\] — LaTeX-mode math
# the template author wrote intentionally. Outside those, escape
# normally.
_LATEX_MATH_RE = re.compile(
    r"(\\\(.*?\\\)|\\\[.*?\\\])",
    flags=re.DOTALL,
)


def _escape_body(raw: str) -> str:
    """Escape LaTeX specials in body prose, preserving ``\\(...\\)`` math.

    Authors who want typeset math inline write ``\\(`` / ``\\)``
    (LaTeX's preferred inline-math delimiters) and the contents go
    through unchanged. Everything else passes through
    :func:`_latex_escape`.
    """
    parts: list[str] = []
    last = 0
    for match in _LATEX_MATH_RE.finditer(raw):
        # Plain text segment before this math span — escape it.
        parts.append(_latex_escape(raw[last:match.start()]))
        # Math span — pass through verbatim.
        parts.append(match.group(0))
        last = match.end()
    parts.append(_latex_escape(raw[last:]))
    return "".join(parts)


def _format_answer_latex(answer: str) -> str:
    """Format the answer for LaTeX — currently escaped plain-text.

    Until the SVG composite path can typeset math too (γ.3 / KaTeX),
    aligning latex / markdown / png on the formatter's canonical
    string form is the only way to keep "the rendered problem
    formula reads the same across every output". Wrapping the
    answer in ``\\(...\\)`` would diverge from the SVG row, which
    has no math-typeset capability today.

    The string still goes through :func:`_latex_escape` so the
    ``$``, ``%``, and ``_`` characters that legitimately appear in
    formatter output (``$1.50``, ``50%``, ``T_ambient``) compile
    cleanly under tectonic.
    """
    if not answer:
        return ""
    return _latex_escape(answer)
