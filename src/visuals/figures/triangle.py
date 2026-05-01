"""γ.3 (A.2) — :class:`TriangleFigure`: labelled triangle with optional overlays.

A general-purpose triangle primitive used by K-12 geometry templates
(angle-sum, congruence, area, similarity) and as a composable building
block for more elaborate figures (e.g. shadow-lengthening could
overlay this on a ground-line). Three vertices are passed in
data-space; the builder auto-fits them into the SVG viewport with a
fixed margin and renders:

- The triangle outline (light grey fill, black stroke).
- Vertex labels at each corner, offset outward away from the centroid.
- Side labels at the midpoint of each side, offset perpendicular to
  the side and away from the centroid.
- Angle labels: a small text near each vertex, on the bisector
  direction, inside the triangle.
- Optional altitudes (dashed), medians (dash-dotted), and angle
  bisectors (dashed) — added imperatively after construction so a
  template can request just the overlays a particular problem needs.

Multi-format rendering follows the γ.3 keystone contract every figure
builder shares with :class:`src.visuals.table.TableSVG`:

- :meth:`to_svg` — self-contained SVG (also returned by :meth:`render`).
- :meth:`to_text` — one-paragraph ASCII description.
- :meth:`to_latex` — TikZ ``\\begin{tikzpicture} ... \\end{tikzpicture}``;
  a near-perfect fit since ``\\draw (A) -- (B) -- (C) -- cycle;`` is
  the canonical TikZ idiom for a triangle.

Determinism: same constructor args + same overlay sequence → byte-
identical SVG. Coordinates resolve to floats formatted via
:func:`_fmt`, which strips trailing zeros so renderers don't shift
strings underneath us.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

from ..base import DEFAULT_FONT, SVGBuilder, _esc, _fmt, _latex_escape


# Default vertex set — a generic right-leaning triangle. Chosen so the
# default render exercises non-trivial geometry (no two sides equal,
# all three angles distinct) while staying easy to read.
_DEFAULT_VERTICES: List[Tuple[float, float]] = [(0.0, 0.0), (4.0, 0.0), (1.0, 3.0)]

# Side keys are *unordered* pairs of vertex names; we use the canonical
# alphabetical orientation so authors writing "AB" and "BA" both hit
# the same dict entry.
_VERTEX_NAMES = ("A", "B", "C")
_SIDE_KEYS = ("AB", "BC", "CA")


class TriangleFigure(SVGBuilder):
    """Labelled triangle with optional altitude / median / angle-bisector overlays.

    Parameters
    ----------
    vertices:
        Three ``(x, y)`` tuples in *data space*. The builder auto-fits
        them into the SVG viewport. The first is "A", second "B",
        third "C".
    side_labels:
        Mapping of side key (``"AB"``, ``"BC"``, ``"CA"``) → label
        text. Missing entries draw no label.
    angle_labels:
        Mapping of vertex name (``"A"``, ``"B"``, ``"C"``) → label
        text rendered inside the triangle near that vertex.
    vertex_labels:
        Mapping of vertex name → corner label. Defaults to the
        vertex's name (so corner A is labelled "A").
    width, height:
        SVG viewport dimensions.
    """

    # Stroke / fill palette — kept as class attributes so subclasses
    # could rebrand without touching render code.
    _TRIANGLE_FILL = "#f5f5f5"
    _TRIANGLE_STROKE = "#000"
    _STROKE_WIDTH = 1.5

    # Overlay strokes. Altitude and angle-bisector are dashed; median is
    # dash-dotted. The patterns are conventional for school geometry
    # diagrams.
    _ALTITUDE_DASH = "6,4"
    _MEDIAN_DASH = "6,3,2,3"
    _BISECTOR_DASH = "4,3"

    # Margin between the data-space bounding box and the SVG viewport
    # edge. Fixed in pixels so labels and arcs have predictable
    # headroom regardless of the viewport size or input scale.
    _MARGIN = 40

    def __init__(
        self,
        vertices: Optional[List[Tuple[float, float]]] = None,
        side_labels: Optional[Dict[str, str]] = None,
        angle_labels: Optional[Dict[str, str]] = None,
        vertex_labels: Optional[Dict[str, str]] = None,
        width: int = 400,
        height: int = 320,
    ):
        super().__init__(width=width, height=height)

        if vertices is None:
            vertices = list(_DEFAULT_VERTICES)
        else:
            vertices = list(vertices)
        if len(vertices) != 3:
            raise ValueError(
                f"TriangleFigure requires exactly 3 vertices, got {len(vertices)}"
            )
        # Cast to float tuples up front so internal geometry math
        # doesn't have to defensively re-cast on every operation.
        self.vertices: List[Tuple[float, float]] = [
            (float(x), float(y)) for x, y in vertices
        ]

        self.side_labels: Dict[str, str] = dict(side_labels or {})
        self.angle_labels: Dict[str, str] = dict(angle_labels or {})
        # Default vertex_labels echo the canonical names so the corners
        # are always labelled even when the author doesn't pass anything.
        self.vertex_labels: Dict[str, str] = {
            "A": "A", "B": "B", "C": "C",
            **(vertex_labels or {}),
        }

        # Overlay registries. Order is preserved (insertion order on
        # dict-typed lists keeps determinism intact across Python
        # versions ≥ 3.7).
        self._altitudes: List[str] = []
        self._medians: List[str] = []
        self._angle_bisectors: List[str] = []

    # ------------------------------------------------------------------
    # Imperative overlay API
    # ------------------------------------------------------------------

    def add_altitude(self, from_vertex: str) -> "TriangleFigure":
        """Add an altitude from ``from_vertex`` to the opposite side.

        Idempotent: adding the same altitude twice keeps a single entry
        in the overlay list, so the SVG output stays deterministic
        regardless of how many times an author calls this.
        """
        self._validate_vertex(from_vertex)
        if from_vertex not in self._altitudes:
            self._altitudes.append(from_vertex)
        return self

    def add_median(self, from_vertex: str) -> "TriangleFigure":
        """Add a median from ``from_vertex`` to the midpoint of the opposite side."""
        self._validate_vertex(from_vertex)
        if from_vertex not in self._medians:
            self._medians.append(from_vertex)
        return self

    def add_angle_bisector(self, from_vertex: str) -> "TriangleFigure":
        """Add an angle bisector from ``from_vertex`` extending to the opposite side."""
        self._validate_vertex(from_vertex)
        if from_vertex not in self._angle_bisectors:
            self._angle_bisectors.append(from_vertex)
        return self

    @staticmethod
    def _validate_vertex(name: str) -> None:
        if name not in _VERTEX_NAMES:
            raise ValueError(
                f"vertex name must be one of {_VERTEX_NAMES}, got {name!r}"
            )

    # ------------------------------------------------------------------
    # Geometry helpers — data-space first, then auto-fit to SVG-space.
    # ------------------------------------------------------------------

    def _bbox(self) -> Tuple[float, float, float, float]:
        """Return ``(min_x, min_y, max_x, max_y)`` over the input vertices."""
        xs = [v[0] for v in self.vertices]
        ys = [v[1] for v in self.vertices]
        return (min(xs), min(ys), max(xs), max(ys))

    def _fit_scale(self) -> Tuple[float, float, float]:
        """Compute (scale, tx, ty) mapping data-space → SVG-space.

        Returns the uniform scale factor plus a pair of translation
        offsets so that the data-space bounding box centres inside
        the viewport with ``self._MARGIN`` px of padding on each side.
        Degenerate (zero-extent) bounding boxes fall back to ``scale=1``
        — a collinear input still renders, just as a single line.
        """
        min_x, min_y, max_x, max_y = self._bbox()
        dx = max_x - min_x
        dy = max_y - min_y
        avail_w = self.width - 2 * self._MARGIN
        avail_h = self.height - 2 * self._MARGIN
        # Uniform scale so the triangle isn't squashed; pick the smaller
        # axis ratio so it fits in both dimensions. Guard against a zero
        # extent (collinear vertices, for instance).
        sx = avail_w / dx if dx > 1e-9 else 1.0
        sy = avail_h / dy if dy > 1e-9 else 1.0
        scale = min(sx, sy)
        if not math.isfinite(scale) or scale <= 0:
            scale = 1.0
        # Centring: project the data-space midpoint to the viewport
        # centre after scaling.
        mid_x = (min_x + max_x) / 2
        mid_y = (min_y + max_y) / 2
        tx = self.width / 2 - scale * mid_x
        # SVG y-axis points down, math y-axis up — flip y when computing
        # the offset so the data-space origin renders right-side-up.
        ty = self.height / 2 + scale * mid_y
        return scale, tx, ty

    def _data_to_px(self, x: float, y: float) -> Tuple[float, float]:
        """Convert a data-space point to SVG-space pixels."""
        scale, tx, ty = self._fit_scale()
        return (scale * x + tx, ty - scale * y)

    def _px_vertices(self) -> List[Tuple[float, float]]:
        """All three vertices in SVG-space."""
        return [self._data_to_px(x, y) for x, y in self.vertices]

    def _centroid_px(self) -> Tuple[float, float]:
        """Centroid of the triangle in SVG-space.

        Used as the "inside" reference for label-offset directions: a
        side label is offset in the direction *away* from the centroid
        so the label sits outside the triangle, not on top of it.
        """
        pxs = self._px_vertices()
        cx = sum(p[0] for p in pxs) / 3
        cy = sum(p[1] for p in pxs) / 3
        return (cx, cy)

    @staticmethod
    def _midpoint(p: Tuple[float, float], q: Tuple[float, float]) -> Tuple[float, float]:
        return ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)

    @staticmethod
    def _norm(v: Tuple[float, float]) -> Tuple[float, float]:
        """Normalise a 2D vector. Returns (0, 0) for the zero vector."""
        n = math.hypot(v[0], v[1])
        if n < 1e-9:
            return (0.0, 0.0)
        return (v[0] / n, v[1] / n)

    @staticmethod
    def _vertex_index(name: str) -> int:
        return _VERTEX_NAMES.index(name)

    def _opposite_side(self, vertex: str) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """Return the two SVG-space endpoints of the side opposite ``vertex``."""
        idx = self._vertex_index(vertex)
        pxs = self._px_vertices()
        # The "opposite" side is the one whose endpoints are the two
        # vertices that aren't ``vertex``.
        others = [pxs[i] for i in range(3) if i != idx]
        return (others[0], others[1])

    @staticmethod
    def _foot_of_perpendicular(
        p: Tuple[float, float],
        a: Tuple[float, float],
        b: Tuple[float, float],
    ) -> Tuple[float, float]:
        """Foot of the perpendicular from ``p`` to the line through ``a`` and ``b``.

        Standard projection formula: parameterise the line as
        ``a + t*(b-a)`` and solve for the ``t`` minimising ``|p - q(t)|``.
        Falls back to ``a`` if ``a == b`` (degenerate side).
        """
        ax, ay = a
        bx, by = b
        dx, dy = bx - ax, by - ay
        denom = dx * dx + dy * dy
        if denom < 1e-9:
            return a
        t = ((p[0] - ax) * dx + (p[1] - ay) * dy) / denom
        return (ax + t * dx, ay + t * dy)

    def _bisector_endpoint(
        self, vertex: str,
    ) -> Optional[Tuple[float, float]]:
        """Endpoint of the angle bisector from ``vertex``, on the opposite side.

        Uses the angle-bisector theorem: the bisector divides the
        opposite side in the ratio of the two adjacent side lengths.
        Returns ``None`` if any adjacent side has zero length (a
        degenerate triangle), so the caller can skip drawing.
        """
        idx = self._vertex_index(vertex)
        pxs = self._px_vertices()
        v = pxs[idx]
        # Opposite-side endpoints in the canonical "next" / "previous"
        # order around the triangle. For vertex A (idx 0), B (idx 1)
        # is "next" and C (idx 2) is "previous", so the opposite side
        # runs from B to C: a point that divides it in ratio AB:AC
        # (measured from B) is the bisector foot.
        b = pxs[(idx + 1) % 3]
        c = pxs[(idx + 2) % 3]
        len_vb = math.hypot(b[0] - v[0], b[1] - v[1])
        len_vc = math.hypot(c[0] - v[0], c[1] - v[1])
        total = len_vb + len_vc
        if total < 1e-9:
            return None
        # Section formula: endpoint = (len_vc * b + len_vb * c) / total.
        # That is: from B, advance toward C by a fraction equal to the
        # opposite-side length ratio. (The bisector hits the opposite
        # side closer to the *shorter* adjacent side.)
        t = len_vb / total
        return (b[0] + t * (c[0] - b[0]), b[1] + t * (c[1] - b[1]))

    # ------------------------------------------------------------------
    # to_svg
    # ------------------------------------------------------------------

    def to_svg(self) -> str:
        parts: List[str] = []
        pxs = self._px_vertices()
        centroid = self._centroid_px()

        # 1. Triangle polygon (fill + stroke).
        poly_pts = " ".join(f"{_fmt(p[0])},{_fmt(p[1])}" for p in pxs)
        parts.append(
            f'<polygon points="{poly_pts}" '
            f'fill="{self._TRIANGLE_FILL}" stroke="{self._TRIANGLE_STROKE}" '
            f'stroke-width="{_fmt(self._STROKE_WIDTH)}"/>'
        )

        # 2. Overlays — drawn before the labels so labels stay readable.
        for name in self._altitudes:
            parts.append(self._render_altitude(name))
        for name in self._medians:
            parts.append(self._render_median(name))
        for name in self._angle_bisectors:
            line = self._render_bisector(name)
            if line:
                parts.append(line)

        # 3. Vertex labels — offset outward (away from centroid) so the
        # text doesn't sit on the triangle stroke.
        for name in _VERTEX_NAMES:
            parts.append(self._render_vertex_label(name, centroid))

        # 4. Side labels — placed at each side's midpoint, offset
        # perpendicular to the side in the direction away from the
        # centroid.
        for key in _SIDE_KEYS:
            text = self.side_labels.get(key)
            if not text:
                continue
            parts.append(self._render_side_label(key, text, centroid))

        # 5. Angle-arc labels — small text near each vertex, biased
        # toward the centroid (i.e. *inside* the triangle).
        for name in _VERTEX_NAMES:
            text = self.angle_labels.get(name)
            if not text:
                continue
            parts.append(self._render_angle_label(name, text, centroid))

        return self._wrap(*parts)

    def _render_altitude(self, vertex: str) -> str:
        """Dashed line from ``vertex`` perpendicular to the opposite side."""
        idx = self._vertex_index(vertex)
        v = self._px_vertices()[idx]
        a, b = self._opposite_side(vertex)
        foot = self._foot_of_perpendicular(v, a, b)
        return (
            f'<line x1="{_fmt(v[0])}" y1="{_fmt(v[1])}" '
            f'x2="{_fmt(foot[0])}" y2="{_fmt(foot[1])}" '
            f'stroke="#000" stroke-width="1" '
            f'stroke-dasharray="{self._ALTITUDE_DASH}"/>'
        )

    def _render_median(self, vertex: str) -> str:
        """Dash-dotted line from ``vertex`` to the midpoint of the opposite side."""
        idx = self._vertex_index(vertex)
        v = self._px_vertices()[idx]
        a, b = self._opposite_side(vertex)
        m = self._midpoint(a, b)
        return (
            f'<line x1="{_fmt(v[0])}" y1="{_fmt(v[1])}" '
            f'x2="{_fmt(m[0])}" y2="{_fmt(m[1])}" '
            f'stroke="#000" stroke-width="1" '
            f'stroke-dasharray="{self._MEDIAN_DASH}"/>'
        )

    def _render_bisector(self, vertex: str) -> Optional[str]:
        """Dashed line from ``vertex`` along the angle bisector, ending on the opposite side."""
        idx = self._vertex_index(vertex)
        v = self._px_vertices()[idx]
        end = self._bisector_endpoint(vertex)
        if end is None:
            return None
        return (
            f'<line x1="{_fmt(v[0])}" y1="{_fmt(v[1])}" '
            f'x2="{_fmt(end[0])}" y2="{_fmt(end[1])}" '
            f'stroke="#000" stroke-width="1" '
            f'stroke-dasharray="{self._BISECTOR_DASH}"/>'
        )

    def _render_vertex_label(
        self, name: str, centroid: Tuple[float, float],
    ) -> str:
        """Vertex name rendered just outside the corner, opposite the centroid."""
        idx = self._vertex_index(name)
        v = self._px_vertices()[idx]
        # Offset direction = unit vector from centroid → vertex. Scale
        # the offset by a fixed pixel amount so labels sit a uniform
        # distance off the corners regardless of triangle size.
        dx, dy = v[0] - centroid[0], v[1] - centroid[1]
        ux, uy = self._norm((dx, dy))
        offset = 14
        lx = v[0] + ux * offset
        ly = v[1] + uy * offset
        # Tweak the y baseline so a label *above* the vertex sits on
        # top of it visually (SVG text anchors at the baseline by
        # default, which sits *below* the y coordinate).
        return (
            f'<text x="{_fmt(lx)}" y="{_fmt(ly + 4)}" '
            f'text-anchor="middle" {DEFAULT_FONT}>'
            f'{_esc(self.vertex_labels.get(name, name))}</text>'
        )

    def _render_side_label(
        self, key: str, text: str, centroid: Tuple[float, float],
    ) -> str:
        """Side label at the midpoint, offset perpendicular outward."""
        a, b = self._side_endpoints(key)
        m = self._midpoint(a, b)
        # Perpendicular direction: rotate (b - a) by 90°. Pick the
        # rotation that points *away from* the centroid — that's the
        # outward perpendicular.
        dx, dy = b[0] - a[0], b[1] - a[1]
        # Two candidate perpendiculars; choose the one whose dot
        # product with (m - centroid) is positive (i.e. it points
        # outward).
        perp_x, perp_y = -dy, dx
        outward = (m[0] - centroid[0], m[1] - centroid[1])
        if perp_x * outward[0] + perp_y * outward[1] < 0:
            perp_x, perp_y = -perp_x, -perp_y
        ux, uy = self._norm((perp_x, perp_y))
        offset = 14
        lx = m[0] + ux * offset
        ly = m[1] + uy * offset
        return (
            f'<text x="{_fmt(lx)}" y="{_fmt(ly + 4)}" '
            f'text-anchor="middle" {DEFAULT_FONT}>'
            f'{_esc(text)}</text>'
        )

    def _side_endpoints(self, key: str) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """Return the two SVG-space vertices that bound side ``key``."""
        # Side key encodes vertex pair; we look up each by name and
        # return them in the order given so the perpendicular rotation
        # in _render_side_label has a deterministic basis.
        a_name, b_name = key[0], key[1]
        pxs = self._px_vertices()
        return (pxs[self._vertex_index(a_name)], pxs[self._vertex_index(b_name)])

    def _render_angle_label(
        self, name: str, text: str, centroid: Tuple[float, float],
    ) -> str:
        """Small text near a vertex, biased toward the centroid (inside the triangle)."""
        idx = self._vertex_index(name)
        v = self._px_vertices()[idx]
        # Direction = vertex → centroid (i.e. *inward*). The angle
        # arc / label naturally sits inside the triangle.
        dx, dy = centroid[0] - v[0], centroid[1] - v[1]
        ux, uy = self._norm((dx, dy))
        offset = 26
        lx = v[0] + ux * offset
        ly = v[1] + uy * offset
        return (
            f'<text x="{_fmt(lx)}" y="{_fmt(ly + 4)}" '
            f'text-anchor="middle" {DEFAULT_FONT}>'
            f'{_esc(text)}</text>'
        )

    # ------------------------------------------------------------------
    # to_text
    # ------------------------------------------------------------------

    def to_text(self) -> str:
        """One-paragraph ASCII description.

        Mentions all three vertices (with their data-space coords),
        any side and angle labels, and any overlays added — so
        downstream alt-text / screen-reader fallbacks have something
        concrete to read.
        """
        verts = ", ".join(
            f"({_fmt(x)}, {_fmt(y)})" for x, y in self.vertices
        )
        # Side label segment — one entry per side, "?" when not labelled
        # so the reader sees that the side exists but is unlabelled.
        side_parts = []
        for key in _SIDE_KEYS:
            label = self.side_labels.get(key, "?")
            side_parts.append(f"{key} = {label}")
        sides_str = "Sides: " + ", ".join(side_parts) + "."

        # Angle label segment — only emit when at least one is set, so
        # the unlabelled-default case stays terse.
        angle_str = ""
        if self.angle_labels:
            angle_parts = [
                f"{name} = {self.angle_labels[name]}"
                for name in _VERTEX_NAMES
                if name in self.angle_labels
            ]
            angle_str = " Angles: " + ", ".join(angle_parts) + "."

        overlay_parts: List[str] = []
        for name in self._altitudes:
            overlay_parts.append(f"altitude from {name}")
        for name in self._medians:
            overlay_parts.append(f"median from {name}")
        for name in self._angle_bisectors:
            overlay_parts.append(f"angle bisector from {name}")
        overlay_str = ""
        if overlay_parts:
            # Capitalise the first overlay token so the sentence reads
            # cleanly even when only one overlay is present.
            joined = ", ".join(overlay_parts)
            overlay_str = " " + joined[0].upper() + joined[1:] + "."

        return (
            f"Triangle ABC with vertices at {verts}. "
            f"{sides_str}{angle_str}{overlay_str}"
        )

    # ------------------------------------------------------------------
    # to_latex (TikZ)
    # ------------------------------------------------------------------

    def to_latex(self) -> str:
        """TikZ rendering.

        Uses the canonical ``\\draw (A) -- (B) -- (C) -- cycle;`` idiom
        so a LaTeX-aware reader sees a familiar shape. Coordinates
        ship in data-space (no auto-fit) — TikZ has its own scaling
        controls (``\\begin{tikzpicture}[scale=...]``) and authors
        typically want to dial those in by hand at template time.
        """
        lines: List[str] = [r"\begin{tikzpicture}"]

        # Define the three named coordinates so subsequent overlays can
        # refer to them symbolically. TikZ accepts unrestricted alpha
        # node names so "(A)", "(B)", "(C)" are clean.
        for name, (x, y) in zip(_VERTEX_NAMES, self.vertices):
            lines.append(
                rf"  \coordinate ({name}) at ({_fmt(x)},{_fmt(y)});"
            )

        # Triangle outline.
        lines.append(r"  \draw[fill=gray!10] (A) -- (B) -- (C) -- cycle;")

        # Overlays. We use TikZ ``calc`` syntax for foot-of-perpendicular
        # and midpoint endpoints to keep this self-contained — but in
        # the interest of a clean, general-audience output we just
        # render the pre-computed endpoints in SVG-pixel space mapped
        # back to the data domain. Simpler: compute in data-space and
        # ship the resulting endpoint coordinates literally.
        for name in self._altitudes:
            foot = self._foot_of_perpendicular_data(name)
            lines.append(
                rf"  \draw[dashed] ({name}) -- "
                rf"({_fmt(foot[0])},{_fmt(foot[1])});"
            )
        for name in self._medians:
            m = self._opposite_midpoint_data(name)
            lines.append(
                rf"  \draw[dash dot] ({name}) -- "
                rf"({_fmt(m[0])},{_fmt(m[1])});"
            )
        for name in self._angle_bisectors:
            end = self._bisector_endpoint_data(name)
            if end is None:
                continue
            lines.append(
                rf"  \draw[dashed] ({name}) -- "
                rf"({_fmt(end[0])},{_fmt(end[1])});"
            )

        # Vertex labels: TikZ's ``node`` syntax glues a label onto a
        # coordinate. We use ``above``/``left``/``right`` heuristics so
        # the label sits on the outward side.
        # Simple rule: place each vertex's label opposite the centroid
        # in data space.
        cx = sum(v[0] for v in self.vertices) / 3
        cy = sum(v[1] for v in self.vertices) / 3
        for name, (x, y) in zip(_VERTEX_NAMES, self.vertices):
            dx, dy = x - cx, y - cy
            anchor = "right" if dx >= 0 else "left"
            if abs(dy) > abs(dx):
                anchor = "above" if dy >= 0 else "below"
            text = self.vertex_labels.get(name, name)
            lines.append(
                rf"  \node[{anchor}] at ({name}) "
                rf"{{{_latex_escape(text)}}};"
            )

        # Side labels: midpoint of each side, default ``[midway]``.
        for key in _SIDE_KEYS:
            text = self.side_labels.get(key)
            if not text:
                continue
            a_name, b_name = key[0], key[1]
            lines.append(
                rf"  \draw ({a_name}) -- ({b_name}) "
                rf"node[midway, above] {{{_latex_escape(text)}}};"
            )

        # Angle labels: a node placed *inside* the triangle, near the
        # vertex along the direction toward the centroid.
        for name in _VERTEX_NAMES:
            text = self.angle_labels.get(name)
            if not text:
                continue
            idx = self._vertex_index(name)
            x, y = self.vertices[idx]
            inward = self._norm((cx - x, cy - y))
            # Step a small amount inward in data-space; 0.4 of one unit
            # is a workable visual offset for typical triangles.
            ax = x + inward[0] * 0.4
            ay = y + inward[1] * 0.4
            lines.append(
                rf"  \node at ({_fmt(ax)},{_fmt(ay)}) "
                rf"{{{_latex_escape(text)}}};"
            )

        lines.append(r"\end{tikzpicture}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Data-space variants of the overlay endpoint helpers (used by TikZ).
    # ------------------------------------------------------------------

    def _foot_of_perpendicular_data(
        self, vertex: str,
    ) -> Tuple[float, float]:
        idx = self._vertex_index(vertex)
        v = self.vertices[idx]
        others = [self.vertices[i] for i in range(3) if i != idx]
        return self._foot_of_perpendicular(v, others[0], others[1])

    def _opposite_midpoint_data(self, vertex: str) -> Tuple[float, float]:
        idx = self._vertex_index(vertex)
        others = [self.vertices[i] for i in range(3) if i != idx]
        return self._midpoint(others[0], others[1])

    def _bisector_endpoint_data(
        self, vertex: str,
    ) -> Optional[Tuple[float, float]]:
        idx = self._vertex_index(vertex)
        v = self.vertices[idx]
        b = self.vertices[(idx + 1) % 3]
        c = self.vertices[(idx + 2) % 3]
        len_vb = math.hypot(b[0] - v[0], b[1] - v[1])
        len_vc = math.hypot(c[0] - v[0], c[1] - v[1])
        total = len_vb + len_vc
        if total < 1e-9:
            return None
        t = len_vb / total
        return (b[0] + t * (c[0] - b[0]), b[1] + t * (c[1] - b[1]))

    # ------------------------------------------------------------------
    # render() default — keeps the visual-sandbox `Visual = ...` contract.
    # ------------------------------------------------------------------

    def render(self) -> str:
        return self.to_svg()


