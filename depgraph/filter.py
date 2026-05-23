"""Filter and prune dependency graphs based on various criteria."""

from __future__ import annotations

from typing import Dict, Set, List, Optional


DependencyGraph = Dict[str, Set[str]]


def filter_by_prefix(graph: DependencyGraph, prefix: str) -> DependencyGraph:
    """Keep only nodes whose names start with the given prefix."""
    filtered: DependencyGraph = {}
    for node, deps in graph.items():
        if node.startswith(prefix):
            filtered[node] = {d for d in deps if d.startswith(prefix)}
    return filtered


def filter_by_depth(graph: DependencyGraph, root: str, max_depth: int) -> DependencyGraph:
    """Return a subgraph containing only nodes reachable from *root* within *max_depth* hops."""
    if root not in graph:
        return {}

    visited: Dict[str, int] = {}
    queue: List[tuple[str, int]] = [(root, 0)]

    while queue:
        node, depth = queue.pop(0)
        if node in visited:
            continue
        visited[node] = depth
        if depth < max_depth:
            for dep in graph.get(node, set()):
                if dep not in visited:
                    queue.append((dep, depth + 1))

    result: DependencyGraph = {}
    for node in visited:
        result[node] = {d for d in graph.get(node, set()) if d in visited}
    return result


def exclude_nodes(graph: DependencyGraph, exclude: List[str]) -> DependencyGraph:
    """Remove specified nodes and any edges referencing them."""
    excluded = set(exclude)
    return {
        node: deps - excluded
        for node, deps in graph.items()
        if node not in excluded
    }


def remove_isolated_nodes(graph: DependencyGraph) -> DependencyGraph:
    """Remove nodes that have no incoming or outgoing edges."""
    all_deps: Set[str] = set()
    for deps in graph.values():
        all_deps.update(deps)

    return {
        node: deps
        for node, deps in graph.items()
        if deps or node in all_deps
    }
