"""Phase β (H1). Approach-B visual builders.

Templates with `visual.format: python` set `Visual = <builder>.render()`
inside a Python source block; the renderer captures that binding and
emits it on the dataset row's `visual.source` field as SVG. Same
downstream path as Approach A — the `mathbot rasterize` step turns the
SVG into a PNG sidecar.

Each builder produces a self-contained `<svg>...</svg>` string sized
in user units (no external CSS, no external fonts) so a dataset SVG
renders identically wherever it lands.

Currently shipped builders cover the P0 build queue
(MATHBOT_PROBLEMS_PROPOSAL_v2.md §7):

- ``PlotSVG`` — function plots with axes/grid/labels for N12 (limits),
  N13 (derivatives applications), N14 (integrals applications), N3
  (quadratics), N15 (ODE solution curves).
- ``TreeSVG`` — branching probability / decision trees for P-N1
  (combinatorial counting), P-N2 (conditional probability), and the
  Bayesian-counting K11 sub-pattern of N1.
- ``MarkovSVG`` — labelled-state diagrams with transition arrows for
  N9 Markov-chain stationary-distribution problems.
- ``CircuitSVG`` — series-RLC circuit schematic for N16 second-order
  ODE problems (sub-pattern (b)).

Other shape families (vectors 2D/3D, conic plots, force diagrams) land
as the first P0/P1 template that needs them is authored — `M1` in the
plan.
"""

from .base import SVGBuilder
from .plot import PlotSVG
from .tree import TreeSVG
from .markov import MarkovSVG
from .circuit import CircuitSVG
from .table import TableSVG, FunctionValueTable, MatrixTable, DataTable
from .figures import (
    SectorFigure,
    ConeNetFigure,
    RiverbankFigure,
    OptimizationRegionFigure,
    RelatedRatesGeometry,
    FunctionGraphFigure,
    AxesAnnotation,
    TriangleFigure,
    # γ.4s — K1 visual primitives + glyph dispatcher
    ObjectArray,
    PatternStrip,
    ClockFace,
    BalanceScale,
    LinearRuler,
    glyph_for,
)

__all__ = [
    "SVGBuilder",
    "PlotSVG",
    "TreeSVG",
    "MarkovSVG",
    "CircuitSVG",
    # γ.3 (A.1) — table builders
    "TableSVG",
    "FunctionValueTable",
    "MatrixTable",
    "DataTable",
    # γ.3 (A.2) — geometric figure builders
    "SectorFigure",
    "ConeNetFigure",
    "RiverbankFigure",
    "OptimizationRegionFigure",
    "RelatedRatesGeometry",
    "FunctionGraphFigure",
    "AxesAnnotation",
    "TriangleFigure",
    # γ.4s — K1 visual primitives
    "ObjectArray",
    "PatternStrip",
    "ClockFace",
    "BalanceScale",
    "LinearRuler",
    "glyph_for",
]
