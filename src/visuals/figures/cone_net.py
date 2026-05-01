"""γ.3 (A.2) — ConeNetFigure: sector-to-cone unfold diagram.

Side-by-side rendering of (left) the flat circular sector that becomes
the cone's lateral surface and (right) the assembled cone (apex up,
base ellipse below). Pedagogically demonstrates that the sector's arc
length equals the cone's base circumference — the gating visual for
the C.1 cup gold-standard.

Geometry summary:
    sector arc length = slant · (sector_angle_deg · π / 180)
    cone base circumference = 2π · base_radius
The label `arc = 2π·r` on the left and `r` on the right show that the
two are the same length, which is the whole point of the figure.

Both halves render in a single SVG canvas via two anchored regions
(left ≈ x∈[0,280], right ≈ x∈[320,600]) with a small "fold" arrow
between them. The cone is drawn as a 2D isometric projection: a
triangle silhouette (apex on the symmetry axis) plus an ellipse for
the visible base front and a dashed back arc for the hidden back.
"""

from __future__ import annotations

import math
from typing import List

from ..base import DEFAULT_FONT, SVGBuilder, _esc, _fmt


class ConeNetFigure(SVGBuilder):
    """Sector-to-cone net.

    Usage::

        fig = ConeNetFigure(slant=10, sector_angle_deg=216,
                            base_radius=6, height=8)
        Visual = fig.render()

    The defaults form a self-consistent cone: with slant 10 and base
    radius 6, the unfolded sector central angle is exactly
    (2π · 6 / 10) · 180/π = 216°, so the geometry matches the
    pedagogical narrative. Authors are responsible for keeping the
    inputs self-consistent — the figure does not enforce it (a P-XX
    template that varies these together stays in control).
    """

    # Layout knobs — picked so default 600×320 canvas leaves enough
    # whitespace for radius / arc / slant labels without clipping.
    _LEFT_REGION = (0, 280)      # x range for the flat sector
    _RIGHT_REGION = (320, 600)   # x range for the assembled cone
    _CONNECTOR_X = (282, 318)    # arrow lives in the gap
    _STROKE = "#222"
    _DASH = "4 3"

    def __init__(
        self,
        slant: float = 10,
        sector_angle_deg: float = 216,
        base_radius: float = 6,
        height: float = 8,
        width: int = 600,
        height_px: int = 320,
    ):
        super().__init__(width=width, height=height_px)
        self.slant = float(slant)
        self.sector_angle_deg = float(sector_angle_deg)
        self.base_radius = float(base_radius)
        self.cone_height = float(height)

    # ------------------------------------------------------------------
    # Left half: flat sector
    # ------------------------------------------------------------------

    def _sector_path(
        self, cx: float, cy: float, r: float, angle_deg: float,
    ) -> str:
        """Build an SVG <path d=...> for a sector of radius `r` centred
        at (cx, cy), opening from the positive x-axis CCW by
        `angle_deg`. SVG y points down, so we flip the angle's sign
        when computing endpoint coordinates so the sector visibly
        sweeps "upward" the way a reader expects.
        """
        # Clamp degenerate inputs so the path always closes cleanly.
        a = max(0.0, min(360.0, angle_deg))
        theta = math.radians(a)
        # Endpoint of the arc (CCW from +x in math convention; flip y
        # for SVG screen coordinates).
        ex = cx + r * math.cos(theta)
        ey = cy - r * math.sin(theta)
        large = 1 if a > 180.0 else 0
        sweep = 0  # CCW in math = anticlockwise = sweep-flag 0 with
        # the y-axis flipped via the negative sin above.
        if a >= 360.0:
            # Full disk — draw as two half-arcs to keep the path valid.
            return (
                f"M {_fmt(cx + r)} {_fmt(cy)} "
                f"A {_fmt(r)} {_fmt(r)} 0 1 0 {_fmt(cx - r)} {_fmt(cy)} "
                f"A {_fmt(r)} {_fmt(r)} 0 1 0 {_fmt(cx + r)} {_fmt(cy)} Z"
            )
        return (
            f"M {_fmt(cx)} {_fmt(cy)} "
            f"L {_fmt(cx + r)} {_fmt(cy)} "
            f"A {_fmt(r)} {_fmt(r)} 0 {large} {sweep} {_fmt(ex)} {_fmt(ey)} Z"
        )

    def _draw_sector(self) -> List[str]:
        x0, x1 = self._LEFT_REGION
        cx = (x0 + x1) / 2
        cy = self.height / 2 + 20  # nudge down so labels above fit
        # Pick a draw-radius that fits the left region with margins.
        avail_w = (x1 - x0) - 40
        avail_h = self.height - 60
        r = max(20.0, min(avail_w / 2, avail_h / 2))

        parts: List[str] = []
        parts.append(
            f'<path d="{self._sector_path(cx, cy, r, self.sector_angle_deg)}" '
            f'fill="#e9f1fb" stroke="{self._STROKE}" stroke-width="1.5"/>'
        )

        # Slant label on the radius edge (along +x from centre).
        slant_mid_x = cx + r / 2
        slant_mid_y = cy - 6
        parts.append(
            f'<text x="{_fmt(slant_mid_x)}" y="{_fmt(slant_mid_y)}" '
            f'text-anchor="middle" {DEFAULT_FONT}>'
            f'slant = {_fmt(self.slant)}</text>'
        )

        # Arc-length annotation near the arc midpoint.
        mid_theta = math.radians(self.sector_angle_deg / 2)
        arc_x = cx + (r + 12) * math.cos(mid_theta)
        arc_y = cy - (r + 12) * math.sin(mid_theta)
        # When the arc midpoint lands above the centre, anchor middle;
        # when on the side, nudge anchor to keep label inside region.
        anchor = "middle"
        if arc_x < x0 + 50:
            anchor = "start"
            arc_x = x0 + 4
        elif arc_x > x1 - 50:
            anchor = "end"
            arc_x = x1 - 4
        parts.append(
            f'<text x="{_fmt(arc_x)}" y="{_fmt(arc_y)}" '
            f'text-anchor="{anchor}" font-style="italic" {DEFAULT_FONT}>'
            f'arc = 2π·r</text>'
        )

        # Central-angle label inside the sector.
        inner_theta = math.radians(self.sector_angle_deg / 2)
        ix = cx + (r * 0.35) * math.cos(inner_theta)
        iy = cy - (r * 0.35) * math.sin(inner_theta)
        parts.append(
            f'<text x="{_fmt(ix)}" y="{_fmt(iy)}" text-anchor="middle" '
            f'fill="#555" {DEFAULT_FONT}>{_fmt(self.sector_angle_deg)}°</text>'
        )

        # Region caption.
        parts.append(
            f'<text x="{_fmt(cx)}" y="20" text-anchor="middle" '
            f'font-style="italic" {DEFAULT_FONT}>flat sector (lateral surface)</text>'
        )
        return parts

    # ------------------------------------------------------------------
    # Right half: assembled cone (2D iso projection)
    # ------------------------------------------------------------------

    def _draw_cone(self) -> List[str]:
        x0, x1 = self._RIGHT_REGION
        cx = (x0 + x1) / 2
        # Pick a vertical scale: the silhouette height should be
        # ~70% of the canvas, base ellipse below the apex.
        avail_h = self.height - 80  # title + base label margins
        avail_w = (x1 - x0) - 40

        # Map cone's geometric height + radius onto pixels with a
        # single scale factor so proportions read correctly. Guard
        # against degenerate base_radius == 0.
        denom = max(self.cone_height, 2.0 * max(self.base_radius, 1e-6))
        scale_h = avail_h / denom
        scale_w = avail_w / max(2.0 * max(self.base_radius, 1e-6), 1.0)
        scale = min(scale_h, scale_w)

        h_px = self.cone_height * scale
        r_px = self.base_radius * scale
        # Vertical ellipse half-axis — pick a small constant ratio so
        # the base reads as "in perspective" without dominating.
        ry_px = max(4.0, r_px * 0.30)

        apex_y = self.height / 2 - h_px / 2 + 10
        base_cy = apex_y + h_px
        apex_x = cx
        left_x = cx - r_px
        right_x = cx + r_px

        parts: List[str] = []

        # Region caption.
        parts.append(
            f'<text x="{_fmt(cx)}" y="20" text-anchor="middle" '
            f'font-style="italic" {DEFAULT_FONT}>assembled cone</text>'
        )

        # Triangle silhouette — apex to base endpoints. Drawn as a
        # polygon so a fill-shading reads. The base segment is
        # logically inside the ellipse, so we close back to apex via
        # the two slant edges only.
        parts.append(
            f'<polygon points="{_fmt(apex_x)},{_fmt(apex_y)} '
            f'{_fmt(left_x)},{_fmt(base_cy)} {_fmt(right_x)},{_fmt(base_cy)}" '
            f'fill="#fff5e0" stroke="{self._STROKE}" stroke-width="1.5"/>'
        )

        # Visible front of the base ellipse: lower half-arc from
        # left endpoint to right endpoint, sweeping below.
        parts.append(
            f'<path d="M {_fmt(left_x)} {_fmt(base_cy)} '
            f'A {_fmt(r_px)} {_fmt(ry_px)} 0 0 0 {_fmt(right_x)} {_fmt(base_cy)}" '
            f'fill="none" stroke="{self._STROKE}" stroke-width="1.5"/>'
        )
        # Hidden back of the base ellipse: upper half-arc, dashed.
        parts.append(
            f'<path d="M {_fmt(left_x)} {_fmt(base_cy)} '
            f'A {_fmt(r_px)} {_fmt(ry_px)} 0 0 1 {_fmt(right_x)} {_fmt(base_cy)}" '
            f'fill="none" stroke="{self._STROKE}" stroke-width="1.2" '
            f'stroke-dasharray="{self._DASH}"/>'
        )

        # Vertical axis of symmetry (dashed) — apex down to base centre.
        parts.append(
            f'<line x1="{_fmt(apex_x)}" y1="{_fmt(apex_y)}" '
            f'x2="{_fmt(apex_x)}" y2="{_fmt(base_cy)}" '
            f'stroke="#888" stroke-width="1" stroke-dasharray="2 3"/>'
        )

        # Slant label on the right slant edge.
        slant_mid_x = (apex_x + right_x) / 2 + 6
        slant_mid_y = (apex_y + base_cy) / 2
        parts.append(
            f'<text x="{_fmt(slant_mid_x)}" y="{_fmt(slant_mid_y)}" '
            f'text-anchor="start" {DEFAULT_FONT}>'
            f'slant = {_fmt(self.slant)}</text>'
        )

        # Height label inside triangle (just right of the symmetry axis).
        parts.append(
            f'<text x="{_fmt(apex_x - 4)}" y="{_fmt((apex_y + base_cy) / 2)}" '
            f'text-anchor="end" {DEFAULT_FONT}>'
            f'h = {_fmt(self.cone_height)}</text>'
        )

        # Base radius label — horizontal radius of the ellipse,
        # drawn as a thin line + label below the base.
        parts.append(
            f'<line x1="{_fmt(apex_x)}" y1="{_fmt(base_cy)}" '
            f'x2="{_fmt(right_x)}" y2="{_fmt(base_cy)}" '
            f'stroke="#555" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{_fmt((apex_x + right_x) / 2)}" '
            f'y="{_fmt(base_cy + 16)}" text-anchor="middle" {DEFAULT_FONT}>'
            f'r = {_fmt(self.base_radius)}</text>'
        )
        return parts

    # ------------------------------------------------------------------
    # Connector: small fold arrow between the two regions
    # ------------------------------------------------------------------

    def _draw_connector(self) -> List[str]:
        x0, x1 = self._CONNECTOR_X
        cy = self.height / 2
        parts: List[str] = []
        # Arrow line + simple triangle head.
        parts.append(
            f'<line x1="{_fmt(x0)}" y1="{_fmt(cy)}" '
            f'x2="{_fmt(x1 - 8)}" y2="{_fmt(cy)}" '
            f'stroke="{self._STROKE}" stroke-width="1.4"/>'
        )
        parts.append(
            f'<polygon points="{_fmt(x1)},{_fmt(cy)} '
            f'{_fmt(x1 - 8)},{_fmt(cy - 4)} {_fmt(x1 - 8)},{_fmt(cy + 4)}" '
            f'fill="{self._STROKE}"/>'
        )
        parts.append(
            f'<text x="{_fmt((x0 + x1) / 2)}" y="{_fmt(cy - 8)}" '
            f'text-anchor="middle" font-style="italic" {DEFAULT_FONT}>fold</text>'
        )
        return parts

    # ------------------------------------------------------------------
    # Public render targets
    # ------------------------------------------------------------------

    def render(self) -> str:
        return self.to_svg()

    def to_svg(self) -> str:
        parts: List[str] = []
        parts.extend(self._draw_sector())
        parts.extend(self._draw_connector())
        parts.extend(self._draw_cone())
        return self._wrap(*parts)

    def to_text(self) -> str:
        return (
            f"Net of a cone: a flat sector with slant height "
            f"{_fmt(self.slant)} and central angle "
            f"{_fmt(self.sector_angle_deg)}° folds into a cone "
            f"with base radius {_fmt(self.base_radius)} and height "
            f"{_fmt(self.cone_height)}."
        )

    def to_latex(self) -> str:
        # TikZ for the sector is straightforward; the cone is a
        # triangle plus an ellipse with a dashed back-arc, which fits
        # in modest TikZ. If anything in the geometry is degenerate
        # (full-disk sector, zero base radius), fall back to fbox so
        # the LaTeX still compiles.
        s = _fmt(self.slant)
        a = self.sector_angle_deg
        r = _fmt(self.base_radius)
        h = _fmt(self.cone_height)
        if a >= 360.0 or self.base_radius <= 0:
            return (
                rf"\fbox{{[Figure: cone net — sector slant {s}, "
                rf"angle {_fmt(a)}°, base radius {r}, height {h}]}}"
            )
        return (
            r"\begin{tikzpicture}[scale=0.4]" + "\n"
            r"  % flat sector (lateral surface)" + "\n"
            rf"  \draw[fill=blue!5] (0,0) -- ({s},0) "
            rf"arc[start angle=0, end angle={_fmt(a)}, radius={s}] -- cycle;" + "\n"
            rf"  \node at ({_fmt(self.slant / 2)},-0.6) {{slant = {s}}};" + "\n"
            r"  % connector" + "\n"
            rf"  \draw[->,thick] ({_fmt(self.slant + 2)},{_fmt(self.slant / 2)}) "
            rf"-- ({_fmt(self.slant + 5)},{_fmt(self.slant / 2)}) node[midway,above] {{fold}};" + "\n"
            r"  % assembled cone (triangle + ellipse base)" + "\n"
            rf"  \begin{{scope}}[shift={{({_fmt(self.slant + 7)},0)}}]" + "\n"
            rf"    \draw[fill=orange!10] (0,{h}) -- ({_fmt(-self.base_radius)},0) "
            rf"-- ({r},0) -- cycle;" + "\n"
            rf"    \draw (0,0) ellipse ({r} and {_fmt(max(0.4, self.base_radius * 0.30))});" + "\n"
            rf"    \node at ({_fmt(self.base_radius / 2)},-0.8) {{r = {r}}};" + "\n"
            rf"    \node at (-0.4,{_fmt(self.cone_height / 2)}) [anchor=east] {{h = {h}}};" + "\n"
            r"  \end{scope}" + "\n"
            r"\end{tikzpicture}"
        )
