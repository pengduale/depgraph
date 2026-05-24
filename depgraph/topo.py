"""Topological sort and layer assignment for dependency graphs."""

from collections import defaultdict, deque
from typing import Dict, List, Optional


def topological_sort(graph: Dict[str, List[str]]) -> Optional[List[str]]:
    """Return nodes in topological order, or None if a cycle exists."""
    in_degree: Dict[str, int] = {node: 0 for node in graph}
    for node, deps in graph.items():
        for dep in deps:
            if dep not in in_degree:
                in_degree[dep] = 0
            in_degree[dep] += 1

    queue = deque(node for node, deg in in_degree.items() if deg == 0)
    order: List[str] = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for dep in graph.get(node, []):
            in_degree[dep] -= 1
            if in_degree[dep] == 0:
                queue.append(dep)

    if len(order) != len(in_degree):
        return None  # cycle detected
    return order


def assign_layers(graph: Dict[str, List[str]]) -> Optional[Dict[str, int]]:
    """Assign each node a layer (0 = root) based on longest path from a root.

    Returns None if the graph contains a cycle.
    """
    order = topological_sort(graph)
    if order is None:
        return None

    all_nodes = set(graph.keys()) | {d for deps in graph.values() for d in deps}
    layer: Dict[str, int] = {node: 0 for node in all_nodes}

    for node in order:
        for dep in graph.get(node, []):
            layer[dep] = max(layer[dep], layer[node] + 1)

    return layer


def layers_to_groups(layer_map: Dict[str, int]) -> Dict[int, List[str]]:
    """Invert a layer map into a dict of layer_index -> sorted list of nodes."""
    groups: Dict[int, List[str]] = defaultdict(list)
    for node, lvl in layer_map.items():
        groups[lvl].append(node)
    return {lvl: sorted(nodes) for lvl, nodes in sorted(groups.items())}
