"""γ.3 (A.2) — :class:`RelatedRatesGeometry`: related-rates scenario figures.

A dispatcher primitive that renders one of five classic related-rates
geometric setups. Gates the C.3 cone-drain gold-standard (the
``cone_draining`` sub-case) and stands in as the figure for the wider
related-rates corpus (ladder-sliding, balloon-inflating, shadow-
lengthening, boat-pulled-to-dock).

Each setup has its own parameter set and rendering logic; a private
``_render_<setup>()`` method is dispatched by the constructor's
``setup`` argument. Constructor kwargs are stashed on the instance so
``to_svg`` / ``to_text`` / ``to_latex`` all see the same data.

Multi-format rendering follows the γ.3 keystone contract every figure
builder shares:

- :meth:`to_svg` — self-contained SVG (also returned by :meth:`render`).
- :meth:`to_text` — one-paragraph ASCII description.
- :meth:`to_latex` — TikZ for every sub-case where the geometry stays
  small; the dispatcher delegates to ``_latex_<setup>()`` so each
  sub-case is responsible for its own LaTeX. None of the five sub-cases
  here exceed a half-dozen TikZ primitives, so all five ship real
  TikZ rather than the ``\\fbox{[Figure: ...]}`` fallback.

Determinism: same constructor args → byte-identical SVG. All geometry
flows through :func:`_fmt`, which strips trailing zeros so renderers
don't shift coordinate strings underneath us.
"""

from __future__ import annotations

import math
from typing import Callable, Dict, List, Tuple

from ..base import DEFAULT_FONT, SVGBuilder, _esc, _fmt, _latex_escape


_VALID_SETUPS = (
    "ladder_sliding",
    "cone_draining",
    "balloon_inflating",
    "shadow_lengthening",
    "boat_pulled_to_dock",
)


# Per-setup default canvas dimensions. A handful of sub-cases need more
# horizontal room (shadow_lengthening fans out across the ground) so we
# size them slightly wider than the 400×320 default.
_DEFAULT_CANVAS: Dict[str, Tuple[int, int]] = {
    "ladder_sliding": (400, 320),
    "cone_draining": (400, 320),
    "balloon_inflating": (400, 320),
    "shadow_lengthening": (480, 320),
    "boat_pulled_to_dock": (440, 320),
}


class RelatedRatesGeometry(SVGBuilder):
    """Dispatcher primitive: 5 classic related-rates geometric setups.

    Parameters
    ----------
    setup:
        One of ``"ladder_sliding"``, ``"cone_draining"``,
        ``"balloon_inflating"``, ``"shadow_lengthening"``,
        ``"boat_pulled_to_dock"``. Validated in ``__init__`` —
        anything else raises :class:`ValueError`.
    **kwargs:
        Setup-specific parameters; see the per-setup sections below.
        Unknown kwargs are accepted silently (so future sub-cases can
        thread extra knobs without breaking older callers), but each
        setup only consults the keys it knows about.

    Sub-case parameters
    -------------------
    ``ladder_sliding`` —
        ``ladder_length`` (default 10), ``base_distance`` (default 6),
        ``label_ladder``, ``label_base``, ``label_height``.

    ``cone_draining`` —
        ``radius_top`` (default 4), ``height`` (default 10),
        ``water_height`` (default 6), ``label_radius``, ``label_height``,
        ``label_water``.

    ``balloon_inflating`` —
        ``radius`` (default 5), ``label_radius``.

    ``shadow_lengthening`` —
        ``pole_height`` (default 15), ``person_height`` (default 6),
        ``person_distance`` (default 10), ``shadow_length`` (default 4),
        ``label_pole``, ``label_person``, ``label_distance``,
        ``label_shadow``.

    ``boat_pulled_to_dock`` —
        ``dock_height`` (default 4), ``rope_length`` (default 10),
        ``boat_distance`` (default 8), ``label_dock``, ``label_rope``,
        ``label_distance``.
    """

    # Stroke / fill palette — kept as class attributes so subclasses
    # could rebrand without touching the per-setup render code.
    _STROKE = "#000"
    _FILL_LIGHT = "#e0e0e0"
    _FILL_WATER = "#cfe6f5"
    _FILL_GROUND = "#d6c8a8"
    _STROKE_WIDTH = 1.5

    def __init__(self, setup: str = "cone_draining", **kwargs):
        if setup not in _VALID_SETUPS:
            raise ValueError(
                f"Unknown setup {setup!r}; expected one of {_VALID_SETUPS}"
            )
        # Allow callers to override canvas explicitly; otherwise pick a
        # sub-case-appropriate default so shadow_lengthening (which fans
        # out horizontally) doesn't crowd against the right edge.
        default_w, default_h = _DEFAULT_CANVAS[setup]
        width = int(kwargs.pop("width", default_w))
        height = int(kwargs.pop("height", default_h))
        super().__init__(width=width, height=height)

        self.setup = setup
        self.params: Dict[str, object] = dict(kwargs)

    # ------------------------------------------------------------------
    # Dispatch tables
    # ------------------------------------------------------------------

    def _svg_dispatch(self) -> Dict[str, Callable[[], str]]:
        return {
            "ladder_sliding": self._render_ladder_sliding,
            "cone_draining": self._render_cone_draining,
            "balloon_inflating": self._render_balloon_inflating,
            "shadow_lengthening": self._render_shadow_lengthening,
            "boat_pulled_to_dock": self._render_boat_pulled_to_dock,
        }

    def _text_dispatch(self) -> Dict[str, Callable[[], str]]:
        return {
            "ladder_sliding": self._text_ladder_sliding,
            "cone_draining": self._text_cone_draining,
            "balloon_inflating": self._text_balloon_inflating,
            "shadow_lengthening": self._text_shadow_lengthening,
            "boat_pulled_to_dock": self._text_boat_pulled_to_dock,
        }

    def _latex_dispatch(self) -> Dict[str, Callable[[], str]]:
        return {
            "ladder_sliding": self._latex_ladder_sliding,
            "cone_draining": self._latex_cone_draining,
            "balloon_inflating": self._latex_balloon_inflating,
            "shadow_lengthening": self._latex_shadow_lengthening,
            "boat_pulled_to_dock": self._latex_boat_pulled_to_dock,
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def to_svg(self) -> str:
        return self._svg_dispatch()[self.setup]()

    def to_text(self) -> str:
        return self._text_dispatch()[self.setup]()

    def to_latex(self) -> str:
        return self._latex_dispatch()[self.setup]()

    def render(self) -> str:
        return self.to_svg()

    # ------------------------------------------------------------------
    # Helpers — small wrappers so each sub-case stays declarative
    # ------------------------------------------------------------------

    def _p(self, key: str, default):
        """Shorthand for `self.params.get(key, default)`."""
        return self.params.get(key, default)

    def _line(self, x1, y1, x2, y2, dashed: bool = False) -> str:
        dash = ' stroke-dasharray="5,4"' if dashed else ""
        return (
            f'<line x1="{_fmt(x1)}" y1="{_fmt(y1)}" '
            f'x2="{_fmt(x2)}" y2="{_fmt(y2)}" '
            f'stroke="{self._STROKE}" stroke-width="{_fmt(self._STROKE_WIDTH)}"{dash}/>'
        )

    def _text(self, x, y, text: str, anchor: str = "middle") -> str:
        return (
            f'<text x="{_fmt(x)}" y="{_fmt(y)}" '
            f'text-anchor="{anchor}" {DEFAULT_FONT}>'
            f'{_esc(text)}</text>'
        )

    # ------------------------------------------------------------------
    # 1. ladder_sliding
    # ------------------------------------------------------------------

    def _render_ladder_sliding(self) -> str:
        ladder_length = float(self._p("ladder_length", 10))
        base_distance = float(self._p("base_distance", 6))
        label_ladder = self._p("label_ladder", "ℓ = 10")
        label_base = self._p("label_base", "x = 6")
        label_height = self._p("label_height", "y")

        # Compute the wall-contact height from a right triangle. Clamp
        # to a sane minimum so a degenerate input (base ≥ ladder) still
        # renders something rather than NaN.
        if base_distance >= ladder_length:
            tri_height = 1.0
        else:
            tri_height = math.sqrt(
                ladder_length * ladder_length - base_distance * base_distance
            )

        # SVG coordinate frame: corner at lower-left of the floor/wall
        # angle. We scale the triangle to fit inside the viewport.
        margin_l = 60
        margin_r = 40
        margin_t = 30
        margin_b = 60

        # Pick a uniform scale so both axes fit.
        scale_x = (self.width - margin_l - margin_r) / max(base_distance, 1.0)
        scale_y = (self.height - margin_t - margin_b) / max(tri_height, 1.0)
        scale = min(scale_x, scale_y)

        corner_x = margin_l
        corner_y = self.height - margin_b
        base_x = corner_x + base_distance * scale
        wall_y = corner_y - tri_height * scale

        parts: List[str] = []
        # Wall (vertical line going up from the corner).
        parts.append(self._line(corner_x, corner_y, corner_x, margin_t))
        # Ground (horizontal line going right from the corner).
        parts.append(self._line(corner_x, corner_y, self.width - margin_r, corner_y))
        # Ladder (diagonal — base on ground at base_x, top on wall at wall_y).
        parts.append(
            f'<line x1="{_fmt(base_x)}" y1="{_fmt(corner_y)}" '
            f'x2="{_fmt(corner_x)}" y2="{_fmt(wall_y)}" '
            f'stroke="{self._STROKE}" stroke-width="{_fmt(self._STROKE_WIDTH + 0.5)}"/>'
        )
        # Right-angle marker at the corner.
        sq = 8
        parts.append(
            f'<polyline points="{_fmt(corner_x + sq)},{_fmt(corner_y)} '
            f'{_fmt(corner_x + sq)},{_fmt(corner_y - sq)} '
            f'{_fmt(corner_x)},{_fmt(corner_y - sq)}" '
            f'fill="none" stroke="{self._STROKE}" stroke-width="1"/>'
        )
        # Labels.
        parts.append(self._text((corner_x + base_x) / 2, corner_y + 22, str(label_base)))
        parts.append(self._text(corner_x - 18, (corner_y + wall_y) / 2, str(label_height), anchor="end"))
        parts.append(
            self._text(
                (base_x + corner_x) / 2 + 14,
                (corner_y + wall_y) / 2 - 4,
                str(label_ladder),
            )
        )
        return self._wrap(*parts)

    def _text_ladder_sliding(self) -> str:
        ladder_length = self._p("ladder_length", 10)
        base_distance = self._p("base_distance", 6)
        return (
            f"A ladder of length {_fmt(float(ladder_length))} leans against a "
            f"vertical wall; its base is {_fmt(float(base_distance))} units from the wall."
        )

    def _latex_ladder_sliding(self) -> str:
        ladder_length = float(self._p("ladder_length", 10))
        base_distance = float(self._p("base_distance", 6))
        label_ladder = str(self._p("label_ladder", "ℓ = 10"))
        label_base = str(self._p("label_base", "x = 6"))
        label_height = str(self._p("label_height", "y"))
        if base_distance >= ladder_length:
            tri_height = 1.0
        else:
            tri_height = math.sqrt(ladder_length ** 2 - base_distance ** 2)
        # Normalise to ≤ 4 cm so the picture fits a printed page.
        scale = 4.0 / max(base_distance, tri_height)
        bx = _fmt(base_distance * scale)
        ty = _fmt(tri_height * scale)
        return (
            "\\begin{tikzpicture}\n"
            f"  \\draw (0,0) -- (0,{ty}); % wall\n"
            f"  \\draw (0,0) -- ({bx},0); % ground\n"
            f"  \\draw[thick] ({bx},0) -- (0,{ty}); % ladder\n"
            f"  \\node[below] at ({_fmt(float(bx) / 2)},0) "
            f"{{{_latex_escape(label_base)}}};\n"
            f"  \\node[left] at (0,{_fmt(float(ty) / 2)}) "
            f"{{{_latex_escape(label_height)}}};\n"
            f"  \\node[above right] at ({_fmt(float(bx) / 2)},{_fmt(float(ty) / 2)}) "
            f"{{{_latex_escape(label_ladder)}}};\n"
            "\\end{tikzpicture}"
        )

    # ------------------------------------------------------------------
    # 2. cone_draining
    # ------------------------------------------------------------------

    def _render_cone_draining(self) -> str:
        radius_top = float(self._p("radius_top", 4))
        cone_height = float(self._p("height", 10))
        water_height = float(self._p("water_height", 6))
        label_radius = self._p("label_radius", "r_top = 4")
        label_height = self._p("label_height", "h = 10")
        label_water = self._p("label_water", "water = 6")

        # Clamp water_height into [0, cone_height] for layout safety.
        wh = max(0.0, min(water_height, cone_height))

        # Cone is point-down. Vertex sits below; rim sits above.
        margin_top = 30
        margin_bot = 50
        margin_x = 40
        plot_h = self.height - margin_top - margin_bot
        plot_w = self.width - 2 * margin_x

        # Pick a scale that fits both axes. Rim diameter is 2*radius_top.
        scale_h = plot_h / max(cone_height, 0.1)
        scale_r = (plot_w / 2) / max(radius_top, 0.1)
        scale = min(scale_h, scale_r)

        rim_w_px = radius_top * scale
        cone_h_px = cone_height * scale

        cx = self.width / 2
        rim_y = margin_top + 14  # leave room for the ellipse top-arc
        vertex_y = rim_y + cone_h_px

        # Water surface — at proportional height from vertex. Similar
        # triangles: water-radius / radius_top = (water_height) / cone_height.
        if cone_height > 0:
            water_radius_px = (wh / cone_height) * rim_w_px
        else:
            water_radius_px = 0.0
        water_surface_y = vertex_y - wh * scale

        parts: List[str] = []

        # Water region (filled triangle from vertex up to surface) —
        # rendered before the cone outline so the outline overprints
        # the fill edges.
        if wh > 0 and water_radius_px > 0:
            parts.append(
                f'<polygon points="'
                f'{_fmt(cx)},{_fmt(vertex_y)} '
                f'{_fmt(cx - water_radius_px)},{_fmt(water_surface_y)} '
                f'{_fmt(cx + water_radius_px)},{_fmt(water_surface_y)}" '
                f'fill="{self._FILL_WATER}" stroke="none"/>'
            )
            # Surface ellipse — slim ellipse to convey the round surface.
            parts.append(
                f'<ellipse cx="{_fmt(cx)}" cy="{_fmt(water_surface_y)}" '
                f'rx="{_fmt(water_radius_px)}" ry="{_fmt(water_radius_px * 0.25)}" '
                f'fill="{self._FILL_WATER}" stroke="{self._STROKE}" '
                f'stroke-width="1"/>'
            )

        # Cone outline: rim ellipse + two slant lines down to vertex.
        # Draw the back half of the rim dashed for a 3-D feel.
        parts.append(
            f'<ellipse cx="{_fmt(cx)}" cy="{_fmt(rim_y)}" '
            f'rx="{_fmt(rim_w_px)}" ry="{_fmt(rim_w_px * 0.25)}" '
            f'fill="none" stroke="{self._STROKE}" '
            f'stroke-width="{_fmt(self._STROKE_WIDTH)}"/>'
        )
        parts.append(self._line(cx - rim_w_px, rim_y, cx, vertex_y))
        parts.append(self._line(cx + rim_w_px, rim_y, cx, vertex_y))

        # Labels.
        parts.append(self._text(cx + rim_w_px + 6, rim_y - 4, str(label_radius), anchor="start"))
        parts.append(self._text(cx + rim_w_px / 2 + 24, (rim_y + vertex_y) / 2, str(label_height), anchor="start"))
        if wh > 0:
            parts.append(self._text(cx, water_surface_y - 6, str(label_water)))

        return self._wrap(*parts)

    def _text_cone_draining(self) -> str:
        return (
            f"A conical tank with top radius {_fmt(float(self._p('radius_top', 4)))} "
            f"and total height {_fmt(float(self._p('height', 10)))}, "
            f"containing water to height {_fmt(float(self._p('water_height', 6)))}."
        )

    def _latex_cone_draining(self) -> str:
        radius_top = float(self._p("radius_top", 4))
        cone_height = float(self._p("height", 10))
        water_height = max(0.0, min(float(self._p("water_height", 6)), cone_height))
        label_radius = str(self._p("label_radius", "r_top = 4"))
        label_height = str(self._p("label_height", "h = 10"))
        label_water = str(self._p("label_water", "water = 6"))
        # Normalise to fit a 4 cm box.
        scale = 4.0 / max(radius_top, cone_height)
        r = _fmt(radius_top * scale)
        h = _fmt(cone_height * scale)
        if cone_height > 0:
            wr = (water_height / cone_height) * radius_top * scale
        else:
            wr = 0.0
        wr_s = _fmt(wr)
        wh_s = _fmt(water_height * scale)
        lines = [
            "\\begin{tikzpicture}",
            f"  \\draw ({r},{h}) -- (0,0) -- (-{r},{h}); % cone slants",
            f"  \\draw ({r},{h}) arc[start angle=0, end angle=180, "
            f"x radius={r}, y radius={_fmt(float(r) * 0.25)}]; % front rim",
            f"  \\draw[dashed] (-{r},{h}) arc[start angle=180, end angle=360, "
            f"x radius={r}, y radius={_fmt(float(r) * 0.25)}]; % back rim",
        ]
        if water_height > 0 and wr > 0:
            lines.append(
                f"  \\fill[blue!20] (0,0) -- ({wr_s},{wh_s}) -- "
                f"(-{wr_s},{wh_s}) -- cycle;"
            )
            lines.append(
                f"  \\draw ({wr_s},{wh_s}) arc[start angle=0, end angle=180, "
                f"x radius={wr_s}, y radius={_fmt(float(wr_s) * 0.25)}];"
            )
        lines.append(
            f"  \\node[right] at ({r},{h}) {{{_latex_escape(label_radius)}}};"
        )
        lines.append(
            f"  \\node[right] at ({_fmt(float(r) / 2)},{_fmt(float(h) / 2)}) "
            f"{{{_latex_escape(label_height)}}};"
        )
        if water_height > 0:
            lines.append(
                f"  \\node[above] at (0,{wh_s}) {{{_latex_escape(label_water)}}};"
            )
        lines.append("\\end{tikzpicture}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # 3. balloon_inflating
    # ------------------------------------------------------------------

    def _render_balloon_inflating(self) -> str:
        radius = float(self._p("radius", 5))
        label_radius = self._p("label_radius", "r = 5")

        cx = self.width / 2
        cy = self.height / 2
        # Pick a px-radius that fills most of the canvas with margin.
        max_r_px = min(self.width, self.height) / 2 - 40
        r_px = max(40.0, min(max_r_px, radius * 12))
        outer_r = r_px * 1.18

        parts: List[str] = []
        # Dashed outer circle — "expanding to here".
        parts.append(
            f'<circle cx="{_fmt(cx)}" cy="{_fmt(cy)}" r="{_fmt(outer_r)}" '
            f'fill="none" stroke="{self._STROKE}" stroke-width="1" '
            f'stroke-dasharray="5,4"/>'
        )
        # Solid current balloon.
        parts.append(
            f'<circle cx="{_fmt(cx)}" cy="{_fmt(cy)}" r="{_fmt(r_px)}" '
            f'fill="{self._FILL_LIGHT}" stroke="{self._STROKE}" '
            f'stroke-width="{_fmt(self._STROKE_WIDTH)}"/>'
        )
        # Center dot.
        parts.append(
            f'<circle cx="{_fmt(cx)}" cy="{_fmt(cy)}" r="2" fill="#000"/>'
        )
        # Radius arrow from center to right edge.
        edge_x = cx + r_px
        parts.append(self._line(cx, cy, edge_x, cy))
        # Arrowhead at edge.
        head = 6
        parts.append(
            f'<polygon points="'
            f'{_fmt(edge_x)},{_fmt(cy)} '
            f'{_fmt(edge_x - head)},{_fmt(cy - head / 2)} '
            f'{_fmt(edge_x - head)},{_fmt(cy + head / 2)}" '
            f'fill="{self._STROKE}"/>'
        )
        # Outward-direction tick (small arrow on the dashed circle, NE).
        diag = math.cos(math.pi / 4)
        op_x = cx + outer_r * diag
        op_y = cy - outer_r * diag
        ip_x = cx + r_px * diag
        ip_y = cy - r_px * diag
        parts.append(self._line(ip_x, ip_y, op_x, op_y))
        parts.append(
            f'<polygon points="'
            f'{_fmt(op_x)},{_fmt(op_y)} '
            f'{_fmt(op_x - head * diag - head * diag)},{_fmt(op_y + head * diag)} '
            f'{_fmt(op_x + head * diag - head * diag)},{_fmt(op_y + head * diag + head * diag)}" '
            f'fill="{self._STROKE}"/>'
        )

        # Label on the radius.
        parts.append(self._text((cx + edge_x) / 2, cy - 6, str(label_radius)))
        return self._wrap(*parts)

    def _text_balloon_inflating(self) -> str:
        return (
            f"A circular balloon with current radius "
            f"{_fmt(float(self._p('radius', 5)))}, expanding outward."
        )

    def _latex_balloon_inflating(self) -> str:
        radius = float(self._p("radius", 5))
        label_radius = str(self._p("label_radius", "r = 5"))
        # Scale to a reasonable cm size.
        r_cm = max(0.8, min(2.5, radius * 0.4))
        r_str = _fmt(r_cm)
        outer = _fmt(r_cm * 1.18)
        return (
            "\\begin{tikzpicture}\n"
            f"  \\draw[dashed] (0,0) circle ({outer});\n"
            f"  \\draw[fill=gray!20] (0,0) circle ({r_str});\n"
            f"  \\fill (0,0) circle (0.05);\n"
            f"  \\draw[->] (0,0) -- ({r_str},0);\n"
            f"  \\node[above] at ({_fmt(r_cm / 2)},0) "
            f"{{{_latex_escape(label_radius)}}};\n"
            "\\end{tikzpicture}"
        )

    # ------------------------------------------------------------------
    # 4. shadow_lengthening
    # ------------------------------------------------------------------

    def _render_shadow_lengthening(self) -> str:
        pole_height = float(self._p("pole_height", 15))
        person_height = float(self._p("person_height", 6))
        person_distance = float(self._p("person_distance", 10))
        shadow_length = float(self._p("shadow_length", 4))
        label_pole = self._p("label_pole", "L = 15")
        label_person = self._p("label_person", "h = 6")
        label_distance = self._p("label_distance", "d = 10")
        label_shadow = self._p("label_shadow", "s = 4")

        margin_l = 50
        margin_r = 40
        margin_t = 40
        margin_b = 60
        plot_w = self.width - margin_l - margin_r
        plot_h = self.height - margin_t - margin_b

        # Total horizontal world span: pole (at x=0) → person → shadow tip.
        world_w = max(person_distance + shadow_length, 1.0)
        world_h = max(pole_height, 1.0)
        scale = min(plot_w / world_w, plot_h / world_h)

        ground_y = self.height - margin_b
        pole_x = margin_l
        person_x = pole_x + person_distance * scale
        shadow_tip_x = person_x + shadow_length * scale
        pole_top_y = ground_y - pole_height * scale
        person_top_y = ground_y - person_height * scale

        parts: List[str] = []
        # Ground.
        parts.append(self._line(margin_l - 10, ground_y, self.width - margin_r + 10, ground_y))
        # Pole (vertical).
        parts.append(self._line(pole_x, ground_y, pole_x, pole_top_y))
        # Light source — small filled circle at the top of the pole.
        parts.append(
            f'<circle cx="{_fmt(pole_x)}" cy="{_fmt(pole_top_y)}" r="4" '
            f'fill="#fffbb1" stroke="{self._STROKE}" stroke-width="1"/>'
        )
        # Person (vertical line).
        parts.append(
            f'<line x1="{_fmt(person_x)}" y1="{_fmt(ground_y)}" '
            f'x2="{_fmt(person_x)}" y2="{_fmt(person_top_y)}" '
            f'stroke="{self._STROKE}" stroke-width="3"/>'
        )
        # Light ray from lamp top → top of person → shadow tip on ground.
        parts.append(
            f'<line x1="{_fmt(pole_x)}" y1="{_fmt(pole_top_y)}" '
            f'x2="{_fmt(shadow_tip_x)}" y2="{_fmt(ground_y)}" '
            f'stroke="#aa7" stroke-width="1" stroke-dasharray="4,3"/>'
        )
        # Shadow segment — bold along the ground from person foot to tip.
        parts.append(
            f'<line x1="{_fmt(person_x)}" y1="{_fmt(ground_y)}" '
            f'x2="{_fmt(shadow_tip_x)}" y2="{_fmt(ground_y)}" '
            f'stroke="{self._STROKE}" stroke-width="3"/>'
        )

        # Labels.
        parts.append(self._text(pole_x - 8, (pole_top_y + ground_y) / 2, str(label_pole), anchor="end"))
        parts.append(self._text(person_x + 8, (person_top_y + ground_y) / 2, str(label_person), anchor="start"))
        parts.append(self._text((pole_x + person_x) / 2, ground_y + 22, str(label_distance)))
        parts.append(self._text((person_x + shadow_tip_x) / 2, ground_y + 22, str(label_shadow)))
        return self._wrap(*parts)

    def _text_shadow_lengthening(self) -> str:
        pole_height = self._p("pole_height", 15)
        person_height = self._p("person_height", 6)
        person_distance = self._p("person_distance", 10)
        shadow_length = self._p("shadow_length", 4)
        return (
            f"A {_fmt(float(pole_height))}-unit pole "
            f"{_fmt(float(person_distance))} units behind a "
            f"{_fmt(float(person_height))}-unit-tall person; "
            f"the person's shadow extends {_fmt(float(shadow_length))} units past their feet."
        )

    def _latex_shadow_lengthening(self) -> str:
        pole_height = float(self._p("pole_height", 15))
        person_height = float(self._p("person_height", 6))
        person_distance = float(self._p("person_distance", 10))
        shadow_length = float(self._p("shadow_length", 4))
        label_pole = str(self._p("label_pole", "L = 15"))
        label_person = str(self._p("label_person", "h = 6"))
        label_distance = str(self._p("label_distance", "d = 10"))
        label_shadow = str(self._p("label_shadow", "s = 4"))
        # Normalise: total world width (person_distance+shadow) → 5 cm.
        world_w = max(person_distance + shadow_length, 1.0)
        scale = 5.0 / max(world_w, pole_height)
        px = _fmt(person_distance * scale)
        sx = _fmt((person_distance + shadow_length) * scale)
        ph = _fmt(pole_height * scale)
        hh = _fmt(person_height * scale)
        return (
            "\\begin{tikzpicture}\n"
            f"  \\draw (-0.2,0) -- ({_fmt(float(sx) + 0.2)},0); % ground\n"
            f"  \\draw (0,0) -- (0,{ph}); % pole\n"
            f"  \\fill (0,{ph}) circle (0.08);\n"
            f"  \\draw[very thick] ({px},0) -- ({px},{hh}); % person\n"
            f"  \\draw[dashed] (0,{ph}) -- ({sx},0); % light ray\n"
            f"  \\draw[very thick] ({px},0) -- ({sx},0); % shadow\n"
            f"  \\node[left] at (0,{_fmt(float(ph) / 2)}) "
            f"{{{_latex_escape(label_pole)}}};\n"
            f"  \\node[right] at ({px},{_fmt(float(hh) / 2)}) "
            f"{{{_latex_escape(label_person)}}};\n"
            f"  \\node[below] at ({_fmt(float(px) / 2)},0) "
            f"{{{_latex_escape(label_distance)}}};\n"
            f"  \\node[below] at ({_fmt((float(px) + float(sx)) / 2)},0) "
            f"{{{_latex_escape(label_shadow)}}};\n"
            "\\end{tikzpicture}"
        )

    # ------------------------------------------------------------------
    # 5. boat_pulled_to_dock
    # ------------------------------------------------------------------

    def _render_boat_pulled_to_dock(self) -> str:
        dock_height = float(self._p("dock_height", 4))
        rope_length = float(self._p("rope_length", 10))
        boat_distance = float(self._p("boat_distance", 8))
        label_dock = self._p("label_dock", "dock")
        label_rope = self._p("label_rope", "ℓ = 10")
        label_distance = self._p("label_distance", "x = 8")

        margin_l = 30
        margin_r = 40
        margin_t = 30
        margin_b = 60
        plot_w = self.width - margin_l - margin_r
        plot_h = self.height - margin_t - margin_b

        world_w = max(boat_distance, 1.0)
        world_h = max(dock_height, 1.0)
        scale = min(plot_w / world_w, plot_h / world_h)

        water_y = self.height - margin_b
        dock_top_y = water_y - dock_height * scale
        dock_left_x = margin_l
        dock_right_x = dock_left_x + 50  # fixed pixel-width rectangle
        boat_x = dock_right_x + boat_distance * scale

        parts: List[str] = []
        # Water surface line.
        parts.append(self._line(margin_l - 10, water_y, self.width - margin_r + 10, water_y))
        # A few wavy strokes for water texture.
        for i in range(4):
            wx = margin_l + 30 + i * 70
            parts.append(
                f'<path d="M {_fmt(wx)} {_fmt(water_y + 8)} '
                f'q 6 -4 12 0 t 12 0" fill="none" stroke="#5a8aaa" stroke-width="1"/>'
            )
        # Dock — small rectangle from water surface up.
        parts.append(
            f'<rect x="{_fmt(dock_left_x)}" y="{_fmt(dock_top_y)}" '
            f'width="{_fmt(dock_right_x - dock_left_x)}" '
            f'height="{_fmt(dock_height * scale)}" '
            f'fill="{self._FILL_GROUND}" stroke="{self._STROKE}" '
            f'stroke-width="{_fmt(self._STROKE_WIDTH)}"/>'
        )
        # Rope from dock-edge (top-right of dock) to boat (on water).
        parts.append(
            f'<line x1="{_fmt(dock_right_x)}" y1="{_fmt(dock_top_y)}" '
            f'x2="{_fmt(boat_x)}" y2="{_fmt(water_y)}" '
            f'stroke="{self._STROKE}" stroke-width="{_fmt(self._STROKE_WIDTH)}"/>'
        )
        # Boat — small trapezoid hull at boat_x on the water.
        boat_w = 28.0
        hull_top_y = water_y - 4
        parts.append(
            f'<polygon points="'
            f'{_fmt(boat_x - boat_w / 2)},{_fmt(hull_top_y)} '
            f'{_fmt(boat_x + boat_w / 2)},{_fmt(hull_top_y)} '
            f'{_fmt(boat_x + boat_w / 2 - 6)},{_fmt(water_y + 6)} '
            f'{_fmt(boat_x - boat_w / 2 + 6)},{_fmt(water_y + 6)}" '
            f'fill="{self._FILL_LIGHT}" stroke="{self._STROKE}" '
            f'stroke-width="{_fmt(self._STROKE_WIDTH)}"/>'
        )

        # Labels.
        parts.append(self._text((dock_left_x + dock_right_x) / 2, dock_top_y - 6, str(label_dock)))
        # Rope label — midpoint, offset above the line.
        rope_mid_x = (dock_right_x + boat_x) / 2
        rope_mid_y = (dock_top_y + water_y) / 2
        parts.append(self._text(rope_mid_x, rope_mid_y - 6, str(label_rope)))
        # Boat-distance label below the water line.
        parts.append(self._text((dock_right_x + boat_x) / 2, water_y + 28, str(label_distance)))
        return self._wrap(*parts)

    def _text_boat_pulled_to_dock(self) -> str:
        return (
            f"A boat on the water {_fmt(float(self._p('boat_distance', 8)))} units from "
            f"a dock that sits {_fmt(float(self._p('dock_height', 4)))} units above the water; "
            f"a rope of length {_fmt(float(self._p('rope_length', 10)))} connects the boat "
            f"to the dock edge."
        )

    def _latex_boat_pulled_to_dock(self) -> str:
        dock_height = float(self._p("dock_height", 4))
        boat_distance = float(self._p("boat_distance", 8))
        label_dock = str(self._p("label_dock", "dock"))
        label_rope = str(self._p("label_rope", "ℓ = 10"))
        label_distance = str(self._p("label_distance", "x = 8"))
        scale = 4.0 / max(boat_distance, dock_height)
        d = _fmt(dock_height * scale)
        bx = _fmt(boat_distance * scale)
        return (
            "\\begin{tikzpicture}\n"
            f"  \\draw (-0.2,0) -- ({_fmt(float(bx) + 0.5)},0); % water\n"
            f"  \\draw[fill=brown!30] (0,0) rectangle (0.6,{d}); % dock\n"
            f"  \\draw ({_fmt(0.6)},{d}) -- ({bx},0); % rope\n"
            f"  \\fill[gray!30] ({_fmt(float(bx) - 0.2)},0) rectangle "
            f"({_fmt(float(bx) + 0.2)},-0.1); % boat\n"
            f"  \\node[above] at (0.3,{d}) {{{_latex_escape(label_dock)}}};\n"
            f"  \\node[above] at ({_fmt((0.6 + float(bx)) / 2)},"
            f"{_fmt(float(d) / 2)}) {{{_latex_escape(label_rope)}}};\n"
            f"  \\node[below] at ({_fmt((0.6 + float(bx)) / 2)},0) "
            f"{{{_latex_escape(label_distance)}}};\n"
            "\\end{tikzpicture}"
        )


