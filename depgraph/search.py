"""Search and query utilities for dependency graphs."""

from __future__ import annotations

from typing import Dict, List, Set

Graph = Dict[str, List[str]]


def find_nodes_by_name(graph: Graph, pattern: str, case_sensitive: bool = False) -> List[str]:
    """Return all node names that contain *pattern* as a substring."""
    if not case_sensitive:
        pattern = pattern.lower()
    results = []
    for node in graph:
        haystack = node if case_sensitive else node.lower()
        if pattern in haystack:
            results.append(node)
    return sorted(results)


def find_paths(graph: Graph, source: str, target: str) -> List[List[str]]:
    """Return all simple paths from *source* to *target* in the dependency graph."""
    if source not in graph or target not in graph:
        return []

    all_paths: List[List[str]] = []

    def dfs(current: str, path: List[str], visited: Set[str]) -> None:
        if current == target:
            all_paths.append(list(path))
            return
        for neighbour in graph.get(current, []):
            if neighbour not in visited:
                visited.add(neighbour)
                path.append(neighbour)
                dfs(neighbour, path, visited)
                path.pop()
                visited.discard(neighbour)

    dfs(source, [source], {source})
    return all_paths


def find_dependents(graph: Graph, target: str) -> List[str]:
    """Return all nodes that directly or transitively depend on *target*."""
    dependents: Set[str] = set()

    def walk(node: str) -> None:
        for candidate, deps in graph.items():
            if node in deps and candidate not in dependents:
                dependents.add(candidate)
                walk(candidate)

    walk(target)
    return sorted(dependents)


def find_dependencies(graph: Graph, source: str) -> List[str]:
    """Return all nodes that *source* directly or transitively depends on."""
    if source not in graph:
        return []

    visited: Set[str] = set()

    def walk(node: str) -> None:
        for dep in graph.get(node, []):
            if dep not in visited:
                visited.add(dep)
                walk(dep)

    walk(source)
    return sorted(visited)
