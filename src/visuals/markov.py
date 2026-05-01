"""Markov-chain state diagram builder for Approach-B visuals.

States are auto-arranged on a circle (so 2-state chains land
horizontally, 3-state form a triangle, 4-state form a square, etc.).
Self-loops and bidirectional transitions render as curved arcs to
avoid overlapping arrows.

Author API::

    m = MarkovSVG()
    m.state("Sunny"); m.state("Rainy")
    m.transition("Sunny", "Sunny", p="0.7")     # self-loop
    m.transition("Sunny", "Rainy", p="0.3")
    m.transition("Rainy", "Sunny", p="0.4")
    m.transition("Rainy", "Rainy", p="0.6")
    Visual = m.render()

Designed for N9 Markov-chain stationary-distribution problems plus
transition-matrix word problems generally.
"""

from __future__ import annotations

import math
from typing import List, Optional, Tuple

from .base import DEFAULT_FONT, SVGBuilder, _esc, _fmt


class MarkovSVG(SVGBuilder):
    """Build a labelled-state diagram with transition arrows."""

    def __init__(self, width: int = 400, height: int = 400):
        super().__init__(width, height)
        self._states: List[str] = []
        self._transitions: List[Tuple[str, str, Optional[str]]] = []
        self._radius = 26  # state-circle radius

    def state(self, name: str) -> "MarkovSVG":
        """Register a state. Layout is computed at render time so
        author-side ordering doesn't matter."""
        if name not in self._states:
            self._states.append(name)
        return self

    def transition(
        self,
        from_state: str,
        to_state: str,
        p: Optional[str] = None,
    ) -> "MarkovSVG":
        """Add a transition arrow with optional probability label.

        Auto-registers either endpoint if not yet declared as a state
        (so a one-call setup like
        `m.transition("A", "B", p="0.5")` works without separate
        `state(...)` calls).
        """
        for s in (from_state, to_state):
            if s not in self._states:
                self._states.append(s)
        self._transitions.append((from_state, to_state, p))
        return self

    # ----- layout -----------------------------------------------------

    def _state_positions(self) -> dict:
        n = len(self._states)
        if n == 0:
            return {}
        cx, cy = self.width / 2, self.height / 2
        layout_r = max(0, min(self.width, self.height) / 2 - self._radius - 20)
        # Single-state case: pin to center.
        if n == 1:
            return {self._states[0]: (cx, cy)}
        positions = {}
        # Start at top (-pi/2) and go clockwise.
        for i, s in enumerate(self._states):
            theta = -math.pi / 2 + i * 2 * math.pi / n
            positions[s] = (
                cx + layout_r * math.cos(theta),
                cy + layout_r * math.sin(theta),
            )
        return positions

    # ----- rendering --------------------------------------------------

    def _arrow_marker_def(self) -> str:
        return (
            '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" '
            'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            '<path d="M 0 0 L 10 5 L 0 10 z" fill="#333"/></marker></defs>'
        )

    def _self_loop(self, x: float, y: float, p: Optional[str]) -> List[str]:
        """Draw a self-loop arc above the state."""
        r = self._radius
        # Loop arcs from (x-r/2, y-r) to (x+r/2, y-r) with a small
        # radius so it sits above the node.
        ax, ay = x - r / 2, y - r
        bx, by = x + r / 2, y - r
        # Cubic bezier control points lift the arc upward.
        c1x, c1y = x - r * 1.3, y - r * 2.3
        c2x, c2y = x + r * 1.3, y - r * 2.3
        out = [
            f'<path d="M {_fmt(ax)} {_fmt(ay)} '
            f'C {_fmt(c1x)} {_fmt(c1y)}, {_fmt(c2x)} {_fmt(c2y)}, '
            f'{_fmt(bx)} {_fmt(by)}" '
            f'fill="none" stroke="#333" stroke-width="1.2" marker-end="url(#arrow)"/>'
        ]
        if p is not None:
            out.append(
                f'<text x="{_fmt(x)}" y="{_fmt(y - r * 2.4)}" '
                f'text-anchor="middle" fill="#06c" {DEFAULT_FONT}>{_esc(p)}</text>'
            )
        return out

    def _straight_or_curved_arrow(
        self,
        x1: float, y1: float, x2: float, y2: float,
        p: Optional[str], curve: bool,
    ) -> List[str]:
        """Draw an arrow from (x1,y1) edge → (x2,y2) edge.

        Stops short of the destination by `radius` so the arrowhead
        lands on the circle perimeter rather than under the node.
        """
        dx, dy = x2 - x1, y2 - y1
        d = math.hypot(dx, dy) or 1.0
        ux, uy = dx / d, dy / d
        # Trim both endpoints to the circle perimeter.
        sx = x1 + ux * self._radius
        sy = y1 + uy * self._radius
        ex = x2 - ux * self._radius
        ey = y2 - uy * self._radius
        out: List[str] = []
        if not curve:
            out.append(
                f'<line x1="{_fmt(sx)}" y1="{_fmt(sy)}" '
                f'x2="{_fmt(ex)}" y2="{_fmt(ey)}" '
                f'stroke="#333" stroke-width="1.2" marker-end="url(#arrow)"/>'
            )
            mx, my = (sx + ex) / 2, (sy + ey) / 2
        else:
            # Bow the arrow perpendicular to the direction so two
            # opposite-direction arrows don't overlap.
            nx, ny = -uy, ux
            offset = 18
            cx_, cy_ = (sx + ex) / 2 + nx * offset, (sy + ey) / 2 + ny * offset
            out.append(
                f'<path d="M {_fmt(sx)} {_fmt(sy)} '
                f'Q {_fmt(cx_)} {_fmt(cy_)} {_fmt(ex)} {_fmt(ey)}" '
                f'fill="none" stroke="#333" stroke-width="1.2" marker-end="url(#arrow)"/>'
            )
            mx, my = cx_, cy_
        if p is not None:
            out.append(
                f'<text x="{_fmt(mx)}" y="{_fmt(my - 4)}" '
                f'text-anchor="middle" fill="#06c" {DEFAULT_FONT}>{_esc(p)}</text>'
            )
        return out

    def render(self) -> str:
        positions = self._state_positions()
        parts: List[str] = [self._arrow_marker_def()]

        # Curve any transition that has a reverse-direction sibling so
        # they don't draw on top of each other.
        directed_pairs = {(a, b) for a, b, _p in self._transitions if a != b}
        for from_s, to_s, p in self._transitions:
            if from_s == to_s:
                if from_s in positions:
                    x, y = positions[from_s]
                    parts.extend(self._self_loop(x, y, p))
                continue
            if from_s not in positions or to_s not in positions:
                continue
            x1, y1 = positions[from_s]
            x2, y2 = positions[to_s]
            curve = (to_s, from_s) in directed_pairs
            parts.extend(self._straight_or_curved_arrow(x1, y1, x2, y2, p, curve))

        # State circles + labels (drawn last so they cover arrow tails
        # that pass through the perimeter).
        for s, (x, y) in positions.items():
            parts.append(
                f'<circle cx="{_fmt(x)}" cy="{_fmt(y)}" r="{self._radius}" '
                f'fill="white" stroke="#222" stroke-width="1.5"/>'
            )
            parts.append(
                f'<text x="{_fmt(x)}" y="{_fmt(y + 5)}" '
                f'text-anchor="middle" {DEFAULT_FONT}>{_esc(s)}</text>'
            )
        return self._wrap(*parts)
