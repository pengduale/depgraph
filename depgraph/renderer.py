"""SVG renderer for dependency graphs."""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple

from depgraph.layout import get_layout, NodePos


DEFAULT_NODE_WIDTH = 140
DEFAULT_NODE_HEIGHT = 36
PADDING = 60


def _layout_nodes(
    graph: Dict[str, List[str]],
    strategy: str = "hierarchical",
    spacing_x: float = 200.0,
    spacing_y: float = 120.0,
) -> NodePos:
    """Compute node positions using the specified layout strategy."""
    return get_layout(strategy, graph, spacing_x=spacing_x, spacing_y=spacing_y)


def _arrow_marker() -> str:
    return (
        '<defs><marker id="arrow" markerWidth="10" markerHeight="7" '
        'refX="10" refY="3.5" orient="auto">'
        '<polygon points="0 0, 10 3.5, 0 7" fill="#555" /></marker></defs>'
    )


def _render_edge(x1: float, y1: float, x2: float, y2: float, css_class: str = "edge") -> str:
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'class="{css_class}" marker-end="url(#arrow)" />'
    )


def _render_node(
    node: str,
    x: float,
    y: float,
    css_class: str = "node",
    width: int = DEFAULT_NODE_WIDTH,
    height: int = DEFAULT_NODE_HEIGHT,
) -> str:
    rx, ry = x - width / 2, y - height / 2
    label = node if len(node) <= 18 else node[:15] + "..."
    return (
        f'<g class="{css_class}" data-node="{node}">'
        f'<rect x="{rx:.1f}" y="{ry:.1f}" width="{width}" height="{height}" rx="6" />'
        f'<text x="{x:.1f}" y="{y + 5:.1f}" text-anchor="middle">{label}</text>'
        f"</g>"
    )


def render_svg(
    graph: Dict[str, List[str]],
    highlighted: Optional[Dict[str, str]] = None,
    layout: str = "hierarchical",
    width: int = 900,
    height: int = 600,
) -> str:
    """Render the dependency graph as an SVG string.

    Args:
        graph: Adjacency list {module: [dependency, ...]}.
        highlighted: Optional map of {node: css_class} for highlighting.
        layout: Layout strategy name ('hierarchical' or 'circular').
        width: SVG canvas width in pixels.
        height: SVG canvas height in pixels.

    Returns:
        SVG document as a string.
    """
    positions = _layout_nodes(graph, strategy=layout)
    highlighted = highlighted or {}

    # Offset so all coordinates are positive with padding
    if positions:
        min_x = min(x for x, _ in positions.values())
        min_y = min(y for _, y in positions.values())
        offset_x = -min_x + PADDING + DEFAULT_NODE_WIDTH / 2
        offset_y = -min_y + PADDING + DEFAULT_NODE_HEIGHT / 2
    else:
        offset_x = offset_y = PADDING

    lines: List[str] = []
    lines.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
    )
    lines.append(_arrow_marker())
    lines.append(
        "<style>"
        ".node rect{fill:#4a90d9;stroke:#2c5f8a;stroke-width:1.5px}"
        ".node text{fill:#fff;font:13px sans-serif}"
        ".node.highlight-focus rect{fill:#e07b39}"
        ".node.highlight-ancestor rect{fill:#7db87d}"
        ".node.highlight-descendant rect{fill:#b07dc8}"
        ".edge{stroke:#555;stroke-width:1.5px;fill:none}"
        "</style>"
    )

    # Draw edges
    for src, deps in graph.items():
        if src not in positions:
            continue
        sx, sy = positions[src]
        sx += offset_x
        sy += offset_y
        for dep in deps:
            if dep not in positions:
                continue
            dx, dy = positions[dep]
            dx += offset_x
            dy += offset_y
            lines.append(_render_edge(sx, sy, dx, dy))

    # Draw nodes
    for node, (x, y) in positions.items():
        cx, cy = x + offset_x, y + offset_y
        css = highlighted.get(node, "node")
        lines.append(_render_node(node, cx, cy, css_class=css))

    lines.append("</svg>")
    return "\n".join(lines)
