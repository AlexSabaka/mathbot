"""Phase γ. Multi-target rendering pipelines.

The Phase β output pipeline produced one form (SVG, optionally
rasterised to PNG). Phase γ widens it: the same rendered problem
is emitted as text / markdown / latex / pdf / svg / png, each
consumed by a different downstream — text for log inspection,
markdown for human review, latex/pdf for the JSON benchmark and
the eventual paper, svg/png for the vision-LM grader.

`MathExpr` is the keystone — every pipeline routes math through
it so the same sympy expression typesets consistently across all
six output forms.
"""

from .mathexpr import MathExpr
from .text import render_text
from .markdown import render_markdown
from .latex import render_latex, latex_escape
from .pdf import render_pdf

__all__ = [
    "MathExpr",
    "render_text",
    "render_markdown",
    "render_latex",
    "render_pdf",
    "latex_escape",
]
