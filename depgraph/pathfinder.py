"""Find and describe paths between nodes in a dependency graph."""

from __future__ import annotations
from typing import Dict, List, Optional, Set

Graph = Dict[str, List[str]]


def shortest_path(graph: Graph, source: str, target: str) -> Optional[List[str]]:
    """Return the shortest path from *source* to *target* using BFS.

    Returns None if no path exists or either node is absent.
    """
    if source not in graph or target not in graph:
        return None
    if source == target:
        return [source]

    visited: Set[str] = {source}
    queue: List[List[str]] = [[source]]

    while queue:
        path = queue.pop(0)
        node = path[-1]
        for neighbour in graph.get(node, []):
            if neighbour == target:
                return path + [neighbour]
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append(path + [neighbour])
    return None


def all_paths(
    graph: Graph,
    source: str,
    target: str,
    max_depth: int = 10,
) -> List[List[str]]:
    """Return all simple paths from *source* to *target* up to *max_depth* hops."""
    if source not in graph or target not in graph:
        return []

    results: List[List[str]] = []

    def dfs(current: str, path: List[str], visited: Set[str]) -> None:
        if len(path) > max_depth + 1:
            return
        if current == target and len(path) > 1:
            results.append(list(path))
            return
        for neighbour in graph.get(current, []):
            if neighbour not in visited:
                visited.add(neighbour)
                path.append(neighbour)
                dfs(neighbour, path, visited)
                path.pop()
                visited.discard(neighbour)

    dfs(source, [source], {source})
    return results


def path_exists(graph: Graph, source: str, target: str) -> bool:
    """Return True if any directed path exists from *source* to *target*."""
    return shortest_path(graph, source, target) is not None


def format_path(path: List[str]) -> str:
    """Return a human-readable representation of a path."""
    return " -> ".join(path)
