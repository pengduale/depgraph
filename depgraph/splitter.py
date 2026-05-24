"""Split a dependency graph into weakly connected components."""

from __future__ import annotations

from typing import Dict, List, Set


Graph = Dict[str, List[str]]


def _all_nodes(graph: Graph) -> Set[str]:
    nodes: Set[str] = set(graph.keys())
    for deps in graph.values():
        nodes.update(deps)
    return nodes


def _build_undirected(graph: Graph) -> Dict[str, Set[str]]:
    """Return an adjacency set treating all edges as undirected."""
    undirected: Dict[str, Set[str]] = {n: set() for n in _all_nodes(graph)}
    for node, deps in graph.items():
        for dep in deps:
            undirected[node].add(dep)
            undirected[dep].add(node)
    return undirected


def split_components(graph: Graph) -> List[Graph]:
    """Return a list of sub-graphs, one per weakly connected component.

    Each sub-graph contains only the nodes and edges that belong to that
    component.  Isolated nodes (no edges at all) appear as single-entry
    dicts with an empty dependency list.
    """
    undirected = _build_undirected(graph)
    visited: Set[str] = set()
    components: List[Set[str]] = []

    for node in sorted(undirected):
        if node in visited:
            continue
        component: Set[str] = set()
        stack = [node]
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            component.add(current)
            stack.extend(undirected[current] - visited)
        components.append(component)

    result: List[Graph] = []
    for component in components:
        sub: Graph = {}
        for node in sorted(component):
            deps = [d for d in graph.get(node, []) if d in component]
            sub[node] = deps
        result.append(sub)
    return result


def largest_component(graph: Graph) -> Graph:
    """Return the largest weakly connected component."""
    parts = split_components(graph)
    if not parts:
        return {}
    return max(parts, key=lambda g: len(g))


def component_count(graph: Graph) -> int:
    """Return the number of weakly connected components."""
    return len(split_components(graph))
