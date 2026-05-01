"""Phase γ.3 (A.2) + γ.4s — figure builders for K9-K12 + K1.

γ.3 A.2 builders are K12-oriented (calculus optimization, related-
rates, conic geometry). γ.4s adds five K1-tuned primitives plus a
shared `ShapeGlyph` helper for rendering small countable items.

Every builder inherits from `..base.SVGBuilder` and ships
`to_svg()` / `to_text()` / `to_latex()` for the multi-format
rendering pipeline (Workstream B). Builders are exported from the
top-level `src.visuals` package and exposed in
`build_visual_sandbox` so templates can call e.g.
`ObjectArray(...)` directly inside `visual.format: python` blocks.
"""

from __future__ import annotations

# γ.3 A.2 — K12-oriented geometric builders
from .sector import SectorFigure
from .cone_net import ConeNetFigure
from .riverbank import RiverbankFigure
from .optimization_region import OptimizationRegionFigure
from .related_rates import RelatedRatesGeometry
from .function_graph import FunctionGraphFigure, AxesAnnotation
from .triangle import TriangleFigure

# γ.4s — K1 visual primitives + glyph helpers
from .shape_glyph import (
    glyph_for,
    circle, rounded_rect, triangle, star, heart, dot,
)
from .object_array import ObjectArray
from .pattern_strip import PatternStrip
from .clock_face import ClockFace
from .balance_scale import BalanceScale
from .linear_ruler import LinearRuler


__all__ = [
    # γ.3 A.2
    "SectorFigure",
    "ConeNetFigure",
    "RiverbankFigure",
    "OptimizationRegionFigure",
    "RelatedRatesGeometry",
    "FunctionGraphFigure",
    "AxesAnnotation",
    "TriangleFigure",
    # γ.4s — glyph helpers
    "glyph_for",
    "circle", "rounded_rect", "triangle", "star", "heart", "dot",
    # γ.4s — K1 builders
    "ObjectArray",
    "PatternStrip",
    "ClockFace",
    "BalanceScale",
    "LinearRuler",
]
