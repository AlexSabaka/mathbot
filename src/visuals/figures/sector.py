"""γ.3 (A.2) — :class:`SectorFigure`: circular sector / pie slice with optional cutout.

Gates the C.1 "cup" gold-standard: a sector with a wedge sliced out
visualises the classic frustum-style cup whose missing volume needs
to be reasoned about. Outside that, the same primitive stands in for
any pie-slice geometry — area-of-a-sector problems, central-angle
problems, fraction-of-a-circle problems.

Multi-format rendering follows the γ.3 keystone contract every figure
builder shares with :class:`src.visuals.table.TableSVG`:

- :meth:`to_svg` — self-contained SVG (also returned by :meth:`render`).
- :meth:`to_text` — one-paragraph ASCII description.
- :meth:`to_latex` — TikZ ``\\begin{tikzpicture} ... \\end{tikzpicture}``.
  TikZ is a clean fit here (``\\draw ... arc[...] -- cycle;`` does most
  of the work), so we ship real TikZ rather than the
  ``\\fbox{[Figure: ...]}`` fallback that more involved figures use.

Determinism: same constructor args → byte-identical SVG. All
geometry resolves to floats formatted through :func:`_fmt`, which
strips trailing zeros so renderers don't shift coordinate strings
underneath us.
"""

from __future__ import annotations

import math
from typing import List, Optional

from ..base import DEFAULT_FONT, SVGBuilder, _esc, _fmt, _latex_escape


class SectorFigure(SVGBuilder):
    """Circular sector with optional cutout-wedge.

    The sector spans from the positive x-axis going *counter-clockwise*
    by ``angle_deg`` (standard math convention — same orientation a
    student sees when they draw θ on a unit-circle diagram). When
    ``cutout_deg > 0`` a smaller wedge is rendered in white over the
    sector, centred on the sector's bisector — this visualises the
    "wedge removed for a cup" framing the C.1 gold-standard relies on.

    Parameters
    ----------
    radius:
        Sector radius in SVG units. Drives both the geometry and the
        viewport sizing margin.
    angle_deg:
        Central angle of the (outer) sector, in degrees. Values
        ≥ 360 collapse to a full disc.
    cutout_deg:
        Central angle of the inner cutout wedge, in degrees. ``0``
        disables the cutout. Clamped to ``angle_deg`` (a cutout can't
        be larger than the sector that contains it).
    label_radius:
        Optional label drawn just outside the bottom straight edge of
        the sector — conventionally something like ``"r = 10 cm"``.
    label_angle:
        Optional label drawn inside the sector, near the vertex along
        the bisector — conventionally ``"θ = 120°"``.
    width, height:
        SVG viewport dimensions.
    """

    # Stroke / fill palette — kept as class attributes so subclasses
    # could rebrand without touching render code.
    _SECTOR_FILL = "#e0e0e0"
    _SECTOR_STROKE = "#000"
    _CUTOUT_FILL = "#ffffff"
    _CUTOUT_STROKE = "#000"
    _STROKE_WIDTH = 1.5

    # Margin between sector edge and SVG viewport edge. Fixed in
    # absolute units rather than as a fraction of radius so labels
    # have predictable headroom regardless of radius.
    _MARGIN = 30

    def __init__(
        self,
        radius: float = 100,
        angle_deg: float = 120,
        cutout_deg: float = 0,
        label_radius: Optional[str] = None,
        label_angle: Optional[str] = None,
        width: int = 320,
        height: int = 320,
    ):
        super().__init__(width=width, height=height)
        if radius <= 0:
            raise ValueError(f"radius must be > 0, got {radius}")
        if angle_deg <= 0:
            raise ValueError(f"angle_deg must be > 0, got {angle_deg}")
        if cutout_deg < 0:
            raise ValueError(f"cutout_deg must be >= 0, got {cutout_deg}")

        self.radius = float(radius)
        # Cap the outer angle at a full circle so the path closes
        # cleanly — 361° and 360° look the same on a disc.
        self.angle_deg = float(min(angle_deg, 360.0))
        # Cap the cutout at the outer angle. Authors who pass
        # cutout_deg == angle_deg get a degenerate "fully-cut" figure
        # that still renders without NaN coordinates.
        self.cutout_deg = float(min(cutout_deg, self.angle_deg))
        self.label_radius = label_radius
        self.label_angle = label_angle

    # ------------------------------------------------------------------
    # Geometry helpers
    # ------------------------------------------------------------------

    def _center(self) -> tuple[float, float]:
        """SVG-space coordinates of the sector vertex.

        Centred horizontally; biased slightly downward so the vertex
        sits a touch below midline — the sector typically opens up-and-
        right, so giving the arc more room above looks more balanced.
        """
        return (self.width / 2, self.height / 2 + self.radius / 4)

    def _polar(self, angle_deg: float, r: Optional[float] = None) -> tuple[float, float]:
        """Convert math-convention polar coords (deg, CCW from +x) to SVG-space.

        SVG y-axis points *down*, math y-axis points *up*, so we negate
        the sin term. The conversion is centralised here so every
        polygon vertex / label position uses the same transform.
        """
        if r is None:
            r = self.radius
        cx, cy = self._center()
        rad = math.radians(angle_deg)
        return (cx + r * math.cos(rad), cy - r * math.sin(rad))

    def _sector_path(self, start_deg: float, sweep_deg: float, r: float) -> str:
        """Build a closed `<path d>` string for a sector spanning ``sweep_deg`` degrees.

        ``A rx ry x-axis-rot large-arc sweep-flag x y`` — see the SVG
        spec. ``large-arc`` is 1 when the arc subtends more than 180°
        and ``sweep-flag`` is 0 because we're going counter-clockwise
        in math convention, which is *clockwise* in SVG's y-down system.

        Special-case: at exactly 360° (a full disc) the start and end
        points coincide and the arc is undefined; we emit two 180° arcs
        instead so the path renders as a complete circle.
        """
        cx, cy = self._center()
        start_x, start_y = self._polar(start_deg, r)
        end_x, end_y = self._polar(start_deg + sweep_deg, r)
        if sweep_deg >= 360.0:
            # Full disc — split into two semi-arcs.
            mid_x, mid_y = self._polar(start_deg + 180, r)
            return (
                f"M {_fmt(cx)} {_fmt(cy)} "
                f"L {_fmt(start_x)} {_fmt(start_y)} "
                f"A {_fmt(r)} {_fmt(r)} 0 1 0 {_fmt(mid_x)} {_fmt(mid_y)} "
                f"A {_fmt(r)} {_fmt(r)} 0 1 0 {_fmt(start_x)} {_fmt(start_y)} "
                f"Z"
            )
        large_arc = 1 if sweep_deg > 180.0 else 0
        # sweep-flag=0: SVG arc drawn in the "negative-angle" direction
        # which corresponds to CCW in our math-convention (y-up) frame.
        return (
            f"M {_fmt(cx)} {_fmt(cy)} "
            f"L {_fmt(start_x)} {_fmt(start_y)} "
            f"A {_fmt(r)} {_fmt(r)} 0 {large_arc} 0 {_fmt(end_x)} {_fmt(end_y)} "
            f"Z"
        )

    # ------------------------------------------------------------------
    # to_svg
    # ------------------------------------------------------------------

    def to_svg(self) -> str:
        parts: List[str] = []

        # Outer sector — sweep starts at the +x axis (0°).
        parts.append(
            f'<path d="{self._sector_path(0.0, self.angle_deg, self.radius)}" '
            f'fill="{self._SECTOR_FILL}" stroke="{self._SECTOR_STROKE}" '
            f'stroke-width="{_fmt(self._STROKE_WIDTH)}"/>'
        )

        # Cutout wedge — centred on the outer sector's bisector so
        # equal slivers remain on either side.
        if self.cutout_deg > 0:
            bisector = self.angle_deg / 2
            cutout_start = bisector - self.cutout_deg / 2
            # Cutout uses a slightly smaller radius so its arc tucks
            # *inside* the outer arc and doesn't overdraw the outer
            # stroke (which would leave a hairline gap on the outer
            # circumference at the cutout edges).
            cutout_r = self.radius * 0.98
            parts.append(
                f'<path d="{self._sector_path(cutout_start, self.cutout_deg, cutout_r)}" '
                f'fill="{self._CUTOUT_FILL}" stroke="{self._CUTOUT_STROKE}" '
                f'stroke-width="{_fmt(self._STROKE_WIDTH)}"/>'
            )

        # Vertex marker — small filled dot. Helps the reader see where
        # the angle vertex actually is (especially when a cutout has
        # eaten the central region).
        cx, cy = self._center()
        parts.append(
            f'<circle cx="{_fmt(cx)}" cy="{_fmt(cy)}" r="2" fill="#000"/>'
        )

        # Radius label — placed just outside the *lower* straight edge
        # (the 0° edge). We offset along the perpendicular so the label
        # doesn't sit on top of the stroke.
        if self.label_radius:
            mid_r = self.radius / 2
            edge_x, edge_y = self._polar(0.0, mid_r)
            # Perpendicular to the 0° edge, pointing "down" in SVG (i.e.
            # away from the sector's interior, which opens upward when
            # angle_deg ≤ 180°).
            label_x = edge_x
            label_y = edge_y + 18
            parts.append(
                f'<text x="{_fmt(label_x)}" y="{_fmt(label_y)}" '
                f'text-anchor="middle" {DEFAULT_FONT}>'
                f'{_esc(self.label_radius)}</text>'
            )

        # Angle label — placed inside the sector along the bisector,
        # close to the vertex so it visually "owns" the angle, not
        # the arc.
        if self.label_angle:
            bisector = self.angle_deg / 2
            # Anchor distance: small fraction of radius keeps the
            # label snug against the vertex even for very narrow
            # sectors. Clamped at 22 px minimum so the label never
            # collides with the vertex dot for tiny radii.
            anchor_r = max(self.radius * 0.28, 22.0)
            lx, ly = self._polar(bisector, anchor_r)
            parts.append(
                f'<text x="{_fmt(lx)}" y="{_fmt(ly)}" '
                f'text-anchor="middle" {DEFAULT_FONT}>'
                f'{_esc(self.label_angle)}</text>'
            )

        return self._wrap(*parts)

    # ------------------------------------------------------------------
    # to_text
    # ------------------------------------------------------------------

    def to_text(self) -> str:
        """One-paragraph ASCII description.

        Mentions both author-supplied parameters (radius, central
        angle, cutout if present) so downstream alt-text and
        screen-reader fallbacks have something concrete to read.
        """
        radius_str = _fmt(self.radius)
        angle_str = _fmt(self.angle_deg)
        if self.cutout_deg > 0:
            cutout_str = _fmt(self.cutout_deg)
            base = (
                f"Sector of radius {radius_str}, central angle {angle_str}°, "
                f"with a {cutout_str}° wedge cut out."
            )
        else:
            base = (
                f"Sector of radius {radius_str}, central angle {angle_str}°."
            )
        extras: List[str] = []
        if self.label_radius:
            extras.append(f"Radius labelled '{self.label_radius}'.")
        if self.label_angle:
            extras.append(f"Angle labelled '{self.label_angle}'.")
        if extras:
            return base + " " + " ".join(extras)
        return base

    # ------------------------------------------------------------------
    # to_latex (TikZ)
    # ------------------------------------------------------------------

    def to_latex(self) -> str:
        """TikZ rendering.

        TikZ exposes ``arc[start angle=..., end angle=..., radius=...]``
        which maps near-perfectly to our parameters, so we ship real
        TikZ rather than the ``\\fbox{[Figure: ...]}`` fallback. The
        radius is converted to centimetres (SVG units / 20) so the
        result fits a typical printed page without overflow.
        """
        # SVG radius units → TikZ cm. 20 SVG-units ≈ 1 cm matches the
        # default raster DPI and keeps a default-sized sector under
        # ~6 cm wide on the page.
        r_cm = self.radius / 20.0
        r_str = _fmt(r_cm)
        angle_str = _fmt(self.angle_deg)
        bisector_str = _fmt(self.angle_deg / 2)

        lines: List[str] = []
        lines.append(r"\begin{tikzpicture}")
        # Outer sector: line from origin to (r,0), arc to angle, close.
        lines.append(
            rf"  \draw[fill=gray!20] (0,0) -- ({r_str},0) "
            rf"arc[start angle=0, end angle={angle_str}, radius={r_str}] "
            rf"-- cycle;"
        )

        if self.cutout_deg > 0:
            cutout_start = self.angle_deg / 2 - self.cutout_deg / 2
            cutout_end = self.angle_deg / 2 + self.cutout_deg / 2
            cutout_r = r_cm * 0.98
            cutout_r_str = _fmt(cutout_r)
            cs_str = _fmt(cutout_start)
            ce_str = _fmt(cutout_end)
            lines.append(
                rf"  \draw[fill=white] (0,0) -- "
                rf"({cs_str}:{cutout_r_str}) "
                rf"arc[start angle={cs_str}, end angle={ce_str}, "
                rf"radius={cutout_r_str}] -- cycle;"
            )

        if self.label_radius:
            # Label at midpoint of the 0° edge, slightly below.
            mid_r_str = _fmt(r_cm / 2)
            lines.append(
                rf"  \node[below] at ({mid_r_str},0) "
                rf"{{{_latex_escape(self.label_radius)}}};"
            )
        if self.label_angle:
            anchor_r_str = _fmt(max(r_cm * 0.28, 0.5))
            lines.append(
                rf"  \node at ({bisector_str}:{anchor_r_str}) "
                rf"{{{_latex_escape(self.label_angle)}}};"
            )

        lines.append(r"\end{tikzpicture}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # render() default — keeps the visual-sandbox `Visual = ...` contract
    # ------------------------------------------------------------------

    def render(self) -> str:
        return self.to_svg()
