"""B.2 markdown-rendering pipeline.

GitHub-Flavored Markdown + GH MathJax subset (``$...$`` inline,
``$$...$$`` block). Tables when γ.3's ``TableSVG.to_markdown()``
lands; for now, body / figure / answer.

Per the γ design questions, the SVG visual is embedded inline as a
``data:image/svg+xml;base64,...`` data URI when ``embed_images=True``
(the default). Pass ``embed_images=False`` to write the SVG to a
sidecar file and reference it by relative path — useful for review
with markdown viewers that don't render data URIs (mostly GitHub-
in-comment, where data URIs over a few KB get stripped).
"""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Dict, Optional

# MathExpr import retained for forward use (template-body math can
# round-trip through it if a caller wants); the answer-render path
# uses plain-string passthrough today — see _format_answer_markdown.
from .mathexpr import MathExpr  # noqa: F401


def render_markdown(
    problem: Dict,
    *,
    show_answer: bool = True,
    embed_images: bool = True,
    image_path: Optional[Path] = None,
) -> str:
    """Render a generated problem dict as GitHub-Flavored Markdown.

    ``embed_images=True`` (default) inlines the visual SVG as a
    base64 data URI. ``embed_images=False`` requires
    ``image_path``: a path (absolute or relative to the markdown
    output) that the caller has written the SVG to. The Markdown
    output uses an ``![alt](path)`` link in that case.

    The Answer is wrapped in inline math (``$...$``) when sympy can
    parse it; otherwise it stays as plain text. ``show_answer=False``
    omits the answer block entirely.
    """
    parts = [problem.get('problem', '').rstrip()]

    visual = problem.get('visual') or {}
    visual_source = visual.get('source')
    alt_text = visual.get('alt_text') or "Figure"
    if visual_source:
        if embed_images:
            data_uri = _svg_to_data_uri(visual_source)
            parts.append(f"\n![{_md_escape_alt(alt_text)}]({data_uri})")
        elif image_path is not None:
            parts.append(f"\n![{_md_escape_alt(alt_text)}]({image_path})")
        # else: visual present but no embed and no path — silently drop.
        # The caller has chosen to skip image rendering; surfacing a
        # broken link is worse than omitting.

    if show_answer:
        answer_str = problem.get('task_params', {}).get('expected_answer', '')
        parts.append(f"\n**Answer:** {_format_answer_markdown(answer_str)}")

    return "\n".join(parts)


def _svg_to_data_uri(svg_source: str) -> str:
    """Wrap an SVG string as a ``data:image/svg+xml;base64,...`` URI.

    Base64 (rather than URL-encoding) because GitHub's markdown
    pipeline normalises URL-encoded SVGs sometimes; base64 round-trips
    untouched. ``utf-8`` encode rather than ``ascii`` because SVGs
    routinely contain Unicode (Greek letters in axis labels, the °
    glyph in temperature plots).
    """
    encoded = base64.b64encode(svg_source.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def _md_escape_alt(text: str) -> str:
    """Escape characters that break markdown link syntax inside ``[alt]``.

    The closing ``]`` is the only character that ends the alt text;
    other markdown syntax (``*``, ``_``) renders italic/bold inside
    alt but doesn't break parsing. Newlines collapse to spaces.
    """
    flat = " ".join(str(text).split())
    return flat.replace("]", "\\]")


def _format_answer_markdown(answer: str) -> str:
    """Format the answer for markdown — currently plain-text passthrough.

    Until the SVG composite path can typeset math too (γ.3 / KaTeX),
    aligning markdown / latex / png on the formatter's canonical
    string form is the only way to keep "the rendered problem
    formula reads the same across every output". Wrapping the
    answer in ``$...$`` here would diverge from the SVG row, which
    has no math-typeset capability today.

    Returning the formatted-answer string verbatim matches:

    - the SVG composite (plain text inside ``<text>`` elements)
    - the text pipeline (plain text)
    - the latex pipeline (escaped plain text)

    When KaTeX integration lands, `MathExpr.to_markdown` will be
    routed back in here AND the SVG composite — keeping the
    "single renderer" invariant that γ.2 review surfaced.
    """
    return answer or ""
