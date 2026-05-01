"""γ.4s — `ShapeGlyph`: simple geometric icons for K1 visual builders.

K1 templates render small countable items — apples, books, blocks,
balls, stars, hearts, plain dots. Rather than ship pictographic SVG
paths per item (TD-γ.4s-1), this module provides six simple geometric
shapes that map onto the K1 prose-item vocabulary via the
:func:`glyph_for` dispatcher. The trade-off is intentional: simple
geometric glyphs render identically across cairosvg / browsers /
TikZ, are deterministic to byte level, and are fast to author/test.
Pictographic upgrade lands later as a like-for-like swap behind
``glyph_for``.

Usage from a builder::

    from .shape_glyph import glyph_for

    glyph = glyph_for("apples")  # → circle
    svg_snippet = glyph(cx=80, cy=40, size=18, fill="#dc2626")

Each glyph function returns a single SVG element snippet (string),
ready to be concatenated into the parent builder's `<svg>...</svg>`
envelope. No glyph emits its own viewport — composition is the
caller's job.

Determinism: every coordinate routes through
:func:`src.visuals.base._fmt`; all decisions are pure functions of
the inputs.
"""

from __future__ import annotations

from typing import Callable, Dict

from ..base import _fmt


# Public glyph signature: (cx, cy, size, fill) -> svg-element string.
Glyph = Callable[[float, float, float, str], str]


# ---------------------------------------------------------------------------
# Six primitive glyphs
# ---------------------------------------------------------------------------

def circle(cx: float, cy: float, size: float, fill: str = "#fb923c") -> str:
    """Filled circle. Stand-in for ball / apple / orange / generic round
    countable items.

    `size` is the diameter of the bounding box; the rendered circle has
    radius `size/2`.
    """
    r = size / 2
    return (
        f'<circle cx="{_fmt(cx)}" cy="{_fmt(cy)}" r="{_fmt(r)}" '
        f'fill="{fill}" stroke="#444" stroke-width="1"/>'
    )


def rounded_rect(cx: float, cy: float, size: float, fill: str = "#60a5fa") -> str:
    """Filled rounded rectangle. Stand-in for book / block / box / card.

    Aspect ratio: 1.2:1 (wider than tall) so it reads as a book/block
    rather than a square. `size` is the longer side.
    """
    w = size
    h = size * 0.83  # 1.0/1.2 ≈ 0.83
    x = cx - w / 2
    y = cy - h / 2
    rx = size * 0.10
    return (
        f'<rect x="{_fmt(x)}" y="{_fmt(y)}" '
        f'width="{_fmt(w)}" height="{_fmt(h)}" '
        f'rx="{_fmt(rx)}" fill="{fill}" stroke="#444" stroke-width="1"/>'
    )


def triangle(cx: float, cy: float, size: float, fill: str = "#34d399") -> str:
    """Equilateral triangle, point up. Stand-in for cone / triangle /
    party-hat / mountain item.

    `size` is the side length; the bounding box is centred on
    (cx, cy).
    """
    half = size / 2
    h = size * 0.866  # equilateral triangle height = √3/2 × side
    apex = (cx, cy - h / 2)
    bottom_left = (cx - half, cy + h / 2)
    bottom_right = (cx + half, cy + h / 2)
    points = (
        f"{_fmt(apex[0])},{_fmt(apex[1])} "
        f"{_fmt(bottom_left[0])},{_fmt(bottom_left[1])} "
        f"{_fmt(bottom_right[0])},{_fmt(bottom_right[1])}"
    )
    return (
        f'<polygon points="{points}" '
        f'fill="{fill}" stroke="#444" stroke-width="1"/>'
    )


def star(cx: float, cy: float, size: float, fill: str = "#facc15") -> str:
    """Five-pointed star. Stand-in for star / sticker.

    `size` is the diameter of the outer-circle bounding box.
    """
    import math

    outer_r = size / 2
    inner_r = outer_r * 0.382  # standard 5-point star ratio (golden)
    pts: list[str] = []
    # Start at the top point (-90°) so the star reads "right-side up".
    for i in range(10):
        angle = -math.pi / 2 + i * math.pi / 5
        r = outer_r if i % 2 == 0 else inner_r
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        pts.append(f"{_fmt(x)},{_fmt(y)}")
    return (
        f'<polygon points="{" ".join(pts)}" '
        f'fill="{fill}" stroke="#444" stroke-width="1"/>'
    )


def heart(cx: float, cy: float, size: float, fill: str = "#f472b6") -> str:
    """Heart outline. Stand-in for heart / love-themed item.

    Built from two cubic Bezier curves meeting at the bottom point;
    `size` is the bounding-box width.
    """
    s = size
    # Reference: heart fits a 1.0×0.9-aspect bounding box centred on
    # (cx, cy). Coordinates derived as offsets from the centre and
    # scaled by `s`.
    top = cy - s * 0.20
    bottom = cy + s * 0.45
    left = cx - s / 2
    right = cx + s / 2
    # Two-arc cubic-bezier heart: start at bottom point, sweep up the
    # right lobe to a top dip, mirror down the left lobe.
    d = (
        f"M {_fmt(cx)} {_fmt(bottom)} "
        f"C {_fmt(cx)} {_fmt(cy + s * 0.10)}, "
        f"{_fmt(right)} {_fmt(cy - s * 0.05)}, "
        f"{_fmt(right)} {_fmt(top)} "
        f"C {_fmt(right)} {_fmt(cy - s * 0.45)}, "
        f"{_fmt(cx)} {_fmt(cy - s * 0.45)}, "
        f"{_fmt(cx)} {_fmt(cy - s * 0.20)} "
        f"C {_fmt(cx)} {_fmt(cy - s * 0.45)}, "
        f"{_fmt(left)} {_fmt(cy - s * 0.45)}, "
        f"{_fmt(left)} {_fmt(top)} "
        f"C {_fmt(left)} {_fmt(cy - s * 0.05)}, "
        f"{_fmt(cx)} {_fmt(cy + s * 0.10)}, "
        f"{_fmt(cx)} {_fmt(bottom)} Z"
    )
    return (
        f'<path d="{d}" fill="{fill}" stroke="#444" stroke-width="1"/>'
    )


def dot(cx: float, cy: float, size: float, fill: str = "#1f2937") -> str:
    """Small filled dot. Stand-in for tight counting (10-frames, dice
    pips, abstract count markers).

    Renders at 35% of `size` so a row of dots reads denser than a row
    of full circles — useful when the count is high (8-10).
    """
    r = size * 0.35 / 2
    return (
        f'<circle cx="{_fmt(cx)}" cy="{_fmt(cy)}" r="{_fmt(r)}" '
        f'fill="{fill}"/>'
    )


# ---------------------------------------------------------------------------
# Prose-item → glyph dispatcher
# ---------------------------------------------------------------------------

# Maps prose strings (singular or plural) to glyph functions. The keys
# are intentionally a small curated set tuned to the K1 corpus item
# pool. Unknown items fall back to `circle` — never raises.
_GLYPH_MAP: Dict[str, Glyph] = {
    # Round / spherical items
    "apple": circle, "apples": circle,
    "orange": circle, "oranges": circle,
    "ball": circle, "balls": circle,
    "marble": circle, "marbles": circle,
    "coin": circle, "coins": circle,
    "egg": circle, "eggs": circle,
    "tomato": circle, "tomatoes": circle,
    # Book / box / block items
    "book": rounded_rect, "books": rounded_rect,
    "block": rounded_rect, "blocks": rounded_rect,
    "box": rounded_rect, "boxes": rounded_rect,
    "card": rounded_rect, "cards": rounded_rect,
    "brick": rounded_rect, "bricks": rounded_rect,
    "cube": rounded_rect, "cubes": rounded_rect,
    # Triangular / pointed items
    "triangle": triangle, "triangles": triangle,
    "cone": triangle, "cones": triangle,
    "hat": triangle, "hats": triangle,
    "tree": triangle, "trees": triangle,
    # Star items
    "star": star, "stars": star,
    "sticker": star, "stickers": star,
    # Heart items
    "heart": heart, "hearts": heart,
    # Generic dots (no item match)
    "dot": dot, "dots": dot,
}


def glyph_for(item_name: str) -> Glyph:
    """Map a prose-item name to a glyph function.

    Lookup is case-insensitive against the singular and plural forms
    in :data:`_GLYPH_MAP`. Falls back to :func:`circle` for unknown
    items so a builder's render path never crashes on an exotic
    prose-item the K1 corpus might add later.
    """
    key = str(item_name).strip().lower()
    return _GLYPH_MAP.get(key, circle)


# Re-export the primitive glyph names for builders that want to call
# the geometric form directly (skipping the dispatcher).
__all__ = [
    "Glyph",
    "circle", "rounded_rect", "triangle", "star", "heart", "dot",
    "glyph_for",
]
