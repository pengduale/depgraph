"""Render dependency graphs as interactive SVG diagrams."""

from typing import Dict, Set
import math

SVG_TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#555" />
    </marker>
  </defs>
  <style>
    .node rect {{ fill: #4a90d9; rx: 6; stroke: #2c5f8a; stroke-width: 1.5; cursor: pointer; }}
    .node rect:hover {{ fill: #357abd; }}
    .node text {{ fill: white; font-family: monospace; font-size: 12px; pointer-events: none; }}
    .edge {{ stroke: #555; stroke-width: 1.5; fill: none; marker-end: url(#arrow); }}
  </style>
{edges}
{nodes}
</svg>"""


def _layout_nodes(modules, width: int, height: int):
    """Arrange nodes in a circle."""
    cx, cy = width / 2, height / 2
    radius = min(width, height) * 0.38
    positions = {}
    n = len(modules)
    for i, name in enumerate(sorted(modules)):
        angle = 2 * math.pi * i / max(n, 1) - math.pi / 2
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        positions[name] = (x, y)
    return positions


def render_svg(graph: Dict[str, Set[str]], width: int = 800, height: int = 600) -> str:
    """Render the dependency graph as an SVG string."""
    modules = list(graph.keys())
    if not modules:
        return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"><text x="20" y="40" font-family="monospace">No modules found.</text></svg>'

    positions = _layout_nodes(modules, width, height)
    node_w, node_h = 120, 32

    edges_svg = []
    for src, deps in graph.items():
        if src not in positions:
            continue
        x1, y1 = positions[src]
        for dep in deps:
            top = dep.split(".")[0]
            target = next((m for m in positions if m == top or m.startswith(top + ".")), None)
            if target:
                x2, y2 = positions[target]
                edges_svg.append(
                    f'  <line class="edge" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" />'
                )

    nodes_svg = []
    for name, (x, y) in positions.items():
        label = name if len(name) <= 14 else "..." + name[-11:]
        rx, ry = x - node_w / 2, y - node_h / 2
        nodes_svg.append(
            f'  <g class="node"><title>{name}</title>'
            f'<rect x="{rx:.1f}" y="{ry:.1f}" width="{node_w}" height="{node_h}" rx="6"/>'
            f'<text x="{x:.1f}" y="{y + 5:.1f}" text-anchor="middle">{label}</text></g>'
        )

    return SVG_TEMPLATE.format(
        width=width,
        height=height,
        edges="\n".join(edges_svg),
        nodes="\n".join(nodes_svg),
    )
