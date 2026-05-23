"""Layout strategies for positioning nodes in the dependency graph."""

from __future__ import annotations
from typing import Dict, List, Tuple


NodePos = Dict[str, Tuple[float, float]]


def layout_hierarchical(graph: Dict[str, List[str]], spacing_x: float = 200.0, spacing_y: float = 120.0) -> NodePos:
    """Assign positions using a top-down hierarchical (layered) layout.

    Nodes with no incoming edges are placed at the top (layer 0).
    Each subsequent layer contains nodes reachable from the previous layer.
    """
    if not graph:
        return {}

    all_nodes = set(graph.keys())
    for deps in graph.values():
        all_nodes.update(deps)

    # Compute in-degree
    in_degree: Dict[str, int] = {n: 0 for n in all_nodes}
    for node, deps in graph.items():
        for dep in deps:
            in_degree[dep] = in_degree.get(dep, 0) + 1

    # BFS layering
    layers: List[List[str]] = []
    visited: set = set()
    current_layer = [n for n in all_nodes if in_degree.get(n, 0) == 0]
    current_layer.sort()

    while current_layer:
        layers.append(current_layer)
        visited.update(current_layer)
        next_layer = []
        for node in current_layer:
            for dep in sorted(graph.get(node, [])):
                if dep not in visited:
                    next_layer.append(dep)
        current_layer = list(dict.fromkeys(next_layer))  # deduplicate, preserve order

    # Any remaining nodes (e.g. in cycles) go in a final layer
    remaining = sorted(all_nodes - visited)
    if remaining:
        layers.append(remaining)

    positions: NodePos = {}
    for layer_idx, layer in enumerate(layers):
        y = layer_idx * spacing_y
        total_width = (len(layer) - 1) * spacing_x
        for node_idx, node in enumerate(layer):
            x = node_idx * spacing_x - total_width / 2
            positions[node] = (x, y)

    return positions


def layout_circular(graph: Dict[str, List[str]], radius: float = 300.0) -> NodePos:
    """Arrange all nodes evenly around a circle."""
    import math

    all_nodes = set(graph.keys())
    for deps in graph.values():
        all_nodes.update(deps)

    nodes = sorted(all_nodes)
    if not nodes:
        return {}

    positions: NodePos = {}
    n = len(nodes)
    for i, node in enumerate(nodes):
        angle = 2 * math.pi * i / n
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        positions[node] = (round(x, 2), round(y, 2))

    return positions


def get_layout(name: str, graph: Dict[str, List[str]], **kwargs) -> NodePos:
    """Return node positions for the named layout strategy."""
    strategies = {
        "hierarchical": layout_hierarchical,
        "circular": layout_circular,
    }
    if name not in strategies:
        raise ValueError(f"Unknown layout '{name}'. Choose from: {list(strategies)}.")
    return strategies[name](graph, **kwargs)
