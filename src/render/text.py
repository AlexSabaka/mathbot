"""B.1 text-rendering pipeline.

Plain-text rendering: body prose + figure alt-text placeholder +
formatted Answer. Math expressions in the Answer are routed through
:class:`~src.render.mathexpr.MathExpr` so a sympy answer surfaces as
``x²·exp(-t)`` rather than the canonical ``x**2*exp(-t)`` fixture
form.

This is the lowest-overhead pipeline — no escape rules, no preamble —
and it's the one the gold-standard verification step opens first
(`cat <stem>.txt | less`). Keeping it boring is a feature.

Body text and ``simplifications:`` are already substituted into
``problem['problem']`` by :class:`TemplateGenerator`, so there's no
template-aware logic in this module.
"""

from __future__ import annotations

from typing import Dict, Optional

# MathExpr retained for forward-use; today's text pipeline passes
# the formatter's answer string straight through. See
# `_format_answer_text` for why.
from .mathexpr import MathExpr  # noqa: F401


def render_text(problem: Dict, *, show_answer: bool = True) -> str:
    """Render a generated problem dict as plain text.

    Output structure::

        <body prose>

        [Figure: <alt-text>]   # only when visual.alt_text is set

        Answer: <answer>       # only when show_answer=True

    The figure placeholder lands between body and answer rather than
    inside the body because the body is locale-aware prose; injecting
    a bracketed marker mid-paragraph would read poorly. Downstream
    consumers that want the figure embedded inline can splice the
    SVG directly via ``problem['visual']['source']``.
    """
    parts = [problem.get('problem', '').rstrip()]

    visual = problem.get('visual') or {}
    alt_text = visual.get('alt_text')
    if alt_text:
        # Collapse newlines so the placeholder stays one logical line
        # in flowed-text consumers (terminal `less`, log readers).
        flat = " ".join(str(alt_text).split())
        parts.append(f"\n[Figure: {flat}]")

    if show_answer:
        answer = problem.get('task_params', {}).get('expected_answer', '')
        parts.append(f"\nAnswer: {_format_answer_text(answer)}")

    return "\n".join(parts)


def _format_answer_text(answer: str) -> str:
    """Format the answer for text output — plain-string passthrough.

    γ.2 review fix: every output format (text / markdown / latex /
    svg / png) uses the formatter's canonical answer string verbatim
    so the rendered formula reads the same across all of them. The
    text pipeline previously applied a Unicode lift (``**2`` → ``²``,
    ``oo`` → ``∞``) that diverged from the SVG composite, which
    splices the answer as plain text into ``<text>`` elements with
    no character substitution. Until that path can do the same lift
    (γ.3+ when it runs through a math-typeset layer), the consistent
    answer is the plain sstr form.
    """
    return answer or ""
