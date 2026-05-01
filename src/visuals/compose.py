"""Compose a single SVG combining problem text + visual + (optional)
answer.

Used by `mathbot generate -o png|svg` to render an inspectable
single-problem image. Templates without a `visual:` block compose
to a body-only SVG so this path also works for K1–K8 visual-less
templates.

Layout (top → bottom):

    ┌──────────────────────────────────────────────┐
    │  problem text (wrapped, serif 16pt)          │
    │  ...                                         │
    │                                              │
    │            [ visual SVG, centered ]          │
    │                                              │
    │  Answer: <value>     (optional)              │
    └──────────────────────────────────────────────┘

No external deps — pure SVG markup. PNG rasterization is the CLI's
job; this module only emits the SVG string.
"""

from __future__ import annotations

import re
from typing import Iterable, List, Optional, Tuple

from .base import DEFAULT_FONT, _esc, _fmt


# ---------------------------------------------------------------------------
# Tunables. Conservative defaults; CLI can override page width via flag.
# ---------------------------------------------------------------------------

_DEFAULT_PAGE_WIDTH = 800
_PADDING = 24
_BODY_FONT_SIZE = 16
_BODY_LINE_HEIGHT = 24            # px per line
_BODY_FONT_FAMILY = "Times New Roman, Times, serif"
_TITLE_FONT_SIZE = 18
_ANSWER_FONT_SIZE = 16
_ANSWER_FONT_FAMILY = "Menlo, Monaco, Consolas, monospace"
_GAP_TEXT_TO_VISUAL = 28
_GAP_VISUAL_TO_ANSWER = 28
# Heuristic char count for line wrap at 16pt serif on ~752px usable
# width (page=800 minus 2*24 padding). Errs slightly wide so short
# lines breathe; long lines clip at the page edge instead of running
# off-page.
_WRAP_COLS = 78


# ---------------------------------------------------------------------------
# Word wrapping
# ---------------------------------------------------------------------------

def _wrap(text: str, cols: int = _WRAP_COLS) -> List[str]:
    """Word-wrap problem prose preserving explicit line breaks.

    The body text comes from `template.template` rendered as Jinja —
    multi-line problem statements are common (e.g. the cooling demo
    has the equation on its own line). Splitting on `\\n` first
    keeps that structure; word-wrap each segment on whitespace.
    """
    out: List[str] = []
    for source_line in text.splitlines():
        if not source_line.strip():
            out.append("")
            continue
        words = source_line.split()
        line = ""
        for word in words:
            candidate = (line + " " + word) if line else word
            if len(candidate) <= cols:
                line = candidate
            else:
                if line:
                    out.append(line)
                # Word longer than `cols`? Emit it anyway — better to
                # overflow visually than drop content.
                line = word
        if line:
            out.append(line)
    return out


# ---------------------------------------------------------------------------
# SVG-in-SVG embedding
# ---------------------------------------------------------------------------

_SVG_OPEN_RE = re.compile(r"<svg\b[^>]*>", re.IGNORECASE | re.DOTALL)
_VIEWBOX_RE = re.compile(
    r'viewBox\s*=\s*"([^"]+)"', re.IGNORECASE,
)
_DIM_RE = re.compile(
    r'\b(width|height)\s*=\s*"([^"]+)"', re.IGNORECASE,
)
_XML_DECL_RE = re.compile(r'^\s*<\?xml[^?]*\?>\s*', re.IGNORECASE)


def _strip_xml_decl(svg: str) -> str:
    """Remove a leading `<?xml ...?>` declaration if present.

    SVG-in-SVG nesting requires an SVG element at the start of the
    embed; the XML declaration would land in the middle of the
    composite document and break parsing.
    """
    return _XML_DECL_RE.sub("", svg, count=1)


def _intrinsic_size(svg: str) -> Tuple[float, float]:
    """Best-effort extraction of an SVG's intrinsic (width, height).

    Reads the `width`/`height` attributes on the outer `<svg>`
    element, falling back to `viewBox` width/height. Defaults to
    `(_DEFAULT_PAGE_WIDTH - 2*_PADDING, 300)` if neither is present
    (no SVG at all → caller shouldn't have called us, but defensive).
    """
    head_match = _SVG_OPEN_RE.search(svg)
    if not head_match:
        return float(_DEFAULT_PAGE_WIDTH - 2 * _PADDING), 300.0
    head = head_match.group(0)

    dims = {k.lower(): v for k, v in _DIM_RE.findall(head)}
    w = _maybe_pixels(dims.get("width"))
    h = _maybe_pixels(dims.get("height"))
    if w is not None and h is not None:
        return w, h

    vb_match = _VIEWBOX_RE.search(head)
    if vb_match:
        parts = vb_match.group(1).replace(",", " ").split()
        if len(parts) == 4:
            try:
                _x, _y, vw, vh = (float(p) for p in parts)
                return (w if w is not None else vw, h if h is not None else vh)
            except ValueError:
                pass
    return (
        w if w is not None else float(_DEFAULT_PAGE_WIDTH - 2 * _PADDING),
        h if h is not None else 300.0,
    )


def _maybe_pixels(value: Optional[str]) -> Optional[float]:
    """Parse an SVG length attribute. Pure number or `<n>px` accepted;
    `%`, `em`, etc. fall back to None so the viewBox path takes over."""
    if value is None:
        return None
    stripped = value.strip().rstrip("px").strip()
    try:
        return float(stripped)
    except ValueError:
        return None


def _replace_size_attrs(svg_open_tag: str, width: float, height: float) -> str:
    """Rewrite the outer `<svg>` tag's width/height to scale the
    embedded visual into the composite. Adds them if absent."""
    out = svg_open_tag

    def _sub(name: str, val: str) -> str:
        nonlocal out
        if re.search(rf'\b{name}\s*=\s*"[^"]*"', out, re.IGNORECASE):
            return re.sub(
                rf'\b{name}\s*=\s*"[^"]*"',
                f'{name}="{val}"',
                out,
                count=1,
                flags=re.IGNORECASE,
            )
        # No attribute — inject before the closing `>`.
        return out.replace(">", f' {name}="{val}">', 1)

    out = _sub("width", _fmt(width))
    out = _sub("height", _fmt(height))
    return out


def _embed_visual(
    visual_svg: str, x: float, y: float, max_width: float,
) -> Tuple[str, float, float]:
    """Return (`<svg ...>...</svg>`, used_width, used_height) for the
    visual nested at (x, y). Scales down to `max_width` preserving
    aspect ratio if the intrinsic width exceeds it.
    """
    inner = _strip_xml_decl(visual_svg).strip()
    if not inner:
        return "", 0.0, 0.0
    intrinsic_w, intrinsic_h = _intrinsic_size(inner)
    if intrinsic_w > max_width:
        scale = max_width / intrinsic_w
        target_w = max_width
        target_h = intrinsic_h * scale
    else:
        target_w = intrinsic_w
        target_h = intrinsic_h

    head_match = _SVG_OPEN_RE.search(inner)
    if not head_match:
        return inner, target_w, target_h
    head_old = head_match.group(0)
    head_new = _replace_size_attrs(head_old, target_w, target_h)
    # Inject x / y into the embedded SVG so it's positioned in the
    # composite without needing a wrapping <g> transform.
    head_new = re.sub(r">$", f' x="{_fmt(x)}" y="{_fmt(y)}">', head_new, count=1)
    rebuilt = inner.replace(head_old, head_new, 1)
    return rebuilt, target_w, target_h


# ---------------------------------------------------------------------------
# Composer
# ---------------------------------------------------------------------------

def compose_problem_svg(
    body: str,
    *,
    visual_svg: Optional[str] = None,
    answer: Optional[str] = None,
    title: Optional[str] = None,
    page_width: int = _DEFAULT_PAGE_WIDTH,
) -> str:
    """Build a composite SVG document for one problem.

    Args:
        body: Rendered problem text (post-Jinja). Multi-line is OK;
            explicit `\\n` breaks are preserved.
        visual_svg: Optional `<svg>...</svg>` string from a
            template's `visual.source` (Phase α/β output, format
            already normalised to `svg`). When None or empty, the
            composite is body-only (still useful for K1–K8
            inspection).
        answer: Optional answer string. When provided, rendered as a
            monospace "Answer: …" line below the visual.
        title: Optional small bold title above the body. Rare; the
            CLI doesn't surface this today but the parameter is
            here for future worksheet-style composition.
        page_width: Composite SVG width in px. Visual is scaled to
            fit `page_width - 2*padding`.

    Returns the full SVG string.
    """
    usable_w = page_width - 2 * _PADDING
    parts: List[str] = []
    cursor_y = _PADDING

    if title:
        parts.append(
            f'<text x="{_PADDING}" y="{cursor_y + _TITLE_FONT_SIZE}" '
            f'font-family="{_BODY_FONT_FAMILY}" font-size="{_TITLE_FONT_SIZE}" '
            f'font-weight="bold" fill="#222">{_esc(title)}</text>'
        )
        cursor_y += _TITLE_FONT_SIZE + 12

    # Body (wrapped). Each rendered line is its own <text> so blank
    # lines naturally render as blank rows.
    body_lines = _wrap(body or "")
    text_top = cursor_y + _BODY_FONT_SIZE  # baseline for first line
    for i, line in enumerate(body_lines):
        baseline_y = text_top + i * _BODY_LINE_HEIGHT
        if line:
            parts.append(
                f'<text x="{_PADDING}" y="{_fmt(baseline_y)}" '
                f'font-family="{_BODY_FONT_FAMILY}" font-size="{_BODY_FONT_SIZE}" '
                f'fill="#222" xml:space="preserve">{_esc(line)}</text>'
            )
    body_height = len(body_lines) * _BODY_LINE_HEIGHT
    cursor_y += body_height

    # Optional visual.
    visual_used_h = 0.0
    if visual_svg and visual_svg.strip():
        cursor_y += _GAP_TEXT_TO_VISUAL
        # Center the visual horizontally.
        # We don't know its scaled width until _embed_visual runs;
        # call once with a placeholder x, then compute the center
        # offset from the returned width.
        embed_at_origin, used_w, used_h = _embed_visual(
            visual_svg, x=0.0, y=cursor_y, max_width=float(usable_w),
        )
        center_x = (page_width - used_w) / 2
        # Re-emit at the centered x (cheap re-call vs string-mutating
        # the head twice).
        embed_centered, _, _ = _embed_visual(
            visual_svg, x=center_x, y=cursor_y, max_width=float(usable_w),
        )
        parts.append(embed_centered)
        cursor_y += used_h
        visual_used_h = used_h

    # Optional answer line.
    if answer is not None and answer != "":
        cursor_y += _GAP_VISUAL_TO_ANSWER if visual_used_h else _GAP_TEXT_TO_VISUAL
        baseline = cursor_y + _ANSWER_FONT_SIZE
        parts.append(
            f'<text x="{_PADDING}" y="{_fmt(baseline)}" '
            f'font-family="{_ANSWER_FONT_FAMILY}" font-size="{_ANSWER_FONT_SIZE}" '
            f'font-weight="bold" fill="#003366">'
            f'{_esc("Answer: " + answer)}</text>'
        )
        cursor_y += _ANSWER_FONT_SIZE

    cursor_y += _PADDING
    page_height = max(int(cursor_y), _PADDING * 2 + _BODY_LINE_HEIGHT)

    head = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{page_width}" height="{page_height}" '
        f'viewBox="0 0 {page_width} {page_height}">'
    )
    bg = f'<rect x="0" y="0" width="{page_width}" height="{page_height}" fill="white"/>'
    return head + bg + "".join(parts) + "</svg>"
