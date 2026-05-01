"""Probability / decision tree builder for Approach-B visuals.

Auto-layout: depth → x (left-to-right), order-among-siblings → y. Each
edge carries an optional probability label (or any string the author
wants); each node carries its own label.

Author API::

    tree = TreeSVG()
    yes = tree.branch("Disease", p="0.04")
    no = tree.branch("Healthy", p="0.96")
    yes.then("Pos", p="0.96"); yes.then("Neg", p="0.04")
    no.then("Pos", p="0.08"); no.then("Neg", p="0.92")
    Visual = tree.render()

Designed for P-N1 / P-N2 (combinatorial counting and conditional
probability) plus the K11 Bayesian-counting sub-pattern of N1.
"""

from __future__ import annotations

from typing import List, Optional

from .base import DEFAULT_FONT, SVGBuilder, _esc, _fmt


class _TreeNode:
    """Internal: tracks one node in the tree.

    `then(...)` returns a child node so authors can chain depth-wise
    (`a.then(b).then(c)`); `branch(...)` on the tree returns a top-level
    node so authors can compose siblings explicitly.
    """

    def __init__(self, label: str, p: Optional[str] = None):
        self.label = label
        self.p = p
        self.children: List["_TreeNode"] = []

    def then(self, label: str, p: Optional[str] = None) -> "_TreeNode":
        child = _TreeNode(label, p)
        self.children.append(child)
        return child

    def leaf_count(self) -> int:
        if not self.children:
            return 1
        return sum(c.leaf_count() for c in self.children)

    def max_depth(self) -> int:
        if not self.children:
            return 0
        return 1 + max(c.max_depth() for c in self.children)


class TreeSVG(SVGBuilder):
    """Build a tree of branches with optional edge probabilities."""

    def __init__(self, width: int = 600, height: int = 400):
        super().__init__(width, height)
        self._roots: List[_TreeNode] = []

    def branch(self, label: str, p: Optional[str] = None) -> _TreeNode:
        """Add a top-level branch and return its node for chaining."""
        node = _TreeNode(label, p)
        self._roots.append(node)
        return node

    # ----- layout -----------------------------------------------------

    def _layout(self):
        """Compute (x, y) per node.

        Strategy: total leaf count drives vertical spacing; depth drives
        horizontal spacing. A virtual `root` collects the top-level
        branches (its own position isn't drawn) so the algorithm doesn't
        special-case the case of multiple top-level siblings.
        """
        total_leaves = max(1, sum(r.leaf_count() for r in self._roots))
        max_depth = max((r.max_depth() for r in self._roots), default=0) + 1
        margin_l, margin_r, margin_t, margin_b = 80, 40, 20, 20
        plot_w = self.width - margin_l - margin_r
        plot_h = self.height - margin_t - margin_b
        # Reserve depth=0 column for an implicit root node anchor on the
        # left so the first edge is visible.
        depth_step = plot_w / max_depth if max_depth > 0 else plot_w
        leaf_step = plot_h / total_leaves
        positions = {}  # id(node) -> (x, y)
        leaf_index = [0]  # mutable counter shared across recursion

        def assign(node: _TreeNode, depth: int) -> float:
            if not node.children:
                y = margin_t + (leaf_index[0] + 0.5) * leaf_step
                leaf_index[0] += 1
            else:
                ys = [assign(c, depth + 1) for c in node.children]
                y = sum(ys) / len(ys)
            x = margin_l + depth * depth_step
            positions[id(node)] = (x, y)
            return y

        # Each top-level branch hangs off depth=1 so the implicit
        # depth=0 column carries the entry-point edges.
        for r in self._roots:
            assign(r, 1)
        # Root anchor (depth=0): vertical center of all top-level branches.
        if self._roots:
            top_ys = [positions[id(r)][1] for r in self._roots]
            root_xy = (margin_l, sum(top_ys) / len(top_ys))
        else:
            root_xy = (margin_l, self.height / 2)
        positions[id(self)] = root_xy
        return positions

    # ----- rendering --------------------------------------------------

    def render(self) -> str:
        positions = self._layout()
        parts: List[str] = []

        def draw(node: _TreeNode, parent: object):
            px, py = positions[id(parent)]
            x, y = positions[id(node)]
            # Edge.
            parts.append(
                f'<line x1="{_fmt(px)}" y1="{_fmt(py)}" '
                f'x2="{_fmt(x)}" y2="{_fmt(y)}" '
                f'stroke="#333" stroke-width="1.2"/>'
            )
            if node.p is not None:
                mx, my = (px + x) / 2, (py + y) / 2
                parts.append(
                    f'<text x="{_fmt(mx)}" y="{_fmt(my - 4)}" '
                    f'text-anchor="middle" fill="#06c" {DEFAULT_FONT}>{_esc(node.p)}</text>'
                )
            # Node circle + label.
            parts.append(
                f'<circle cx="{_fmt(x)}" cy="{_fmt(y)}" r="4" fill="#222"/>'
            )
            parts.append(
                f'<text x="{_fmt(x + 8)}" y="{_fmt(y + 4)}" {DEFAULT_FONT}>{_esc(node.label)}</text>'
            )
            for c in node.children:
                draw(c, node)

        for r in self._roots:
            draw(r, self)

        # Root marker (small circle so the entry-point edges land on a
        # visible anchor rather than a bare line).
        rx, ry = positions[id(self)]
        parts.insert(
            0,
            f'<circle cx="{_fmt(rx)}" cy="{_fmt(ry)}" r="3" fill="#666"/>',
        )

        return self._wrap(*parts)
