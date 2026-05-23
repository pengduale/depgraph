"""Graph pruning utilities: remove redundant edges and trim leaf/root nodes."""

from __future__ import annotations

from typing import Dict, List, Set

Graph = Dict[str, List[str]]


def remove_transitive_edges(graph: Graph) -> Graph:
    """Remove edges that are redundant due to transitivity.

    An edge A -> C is redundant if there is already a path A -> ... -> C
    through at least one intermediate node.
    """
    result: Graph = {node: [] for node in graph}

    for src, direct_deps in graph.items():
        for dep in direct_deps:
            # Check if dep is reachable from src WITHOUT the direct edge
            if not _reachable_without(graph, src, dep, direct_dep=dep):
                result[src].append(dep)

    return result


def _reachable_without(graph: Graph, src: str, target: str, direct_dep: str) -> bool:
    """Return True if *target* is reachable from *src* via an indirect path.

    The direct edge src -> direct_dep is ignored so we look for a path of
    length >= 2.
    """
    visited: Set[str] = set()
    stack = [
        nbr for nbr in graph.get(src, []) if nbr != direct_dep
    ]
    while stack:
        node = stack.pop()
        if node == target:
            return True
        if node in visited:
            continue
        visited.add(node)
        stack.extend(graph.get(node, []))
    return False


def trim_leaves(graph: Graph, passes: int = 1) -> Graph:
    """Remove leaf nodes (nodes with no outgoing edges and no dependents).

    Repeats *passes* times so that newly exposed leaves are also removed.
    """
    result = {node: list(deps) for node, deps in graph.items()}
    for _ in range(passes):
        # Nodes that are depended upon by at least one other node
        depended_on: Set[str] = set()
        for deps in result.values():
            depended_on.update(deps)
        to_remove = [
            node for node, deps in result.items()
            if not deps and node not in depended_on
        ]
        for node in to_remove:
            del result[node]
        if not to_remove:
            break
    return result


def trim_roots(graph: Graph, passes: int = 1) -> Graph:
    """Remove root nodes (nodes that no other node depends on and that have deps).

    Repeats *passes* times so that newly exposed roots are also removed.
    """
    result = {node: list(deps) for node, deps in graph.items()}
    for _ in range(passes):
        depended_on: Set[str] = set()
        for deps in result.values():
            depended_on.update(deps)
        to_remove = [
            node for node, deps in result.items()
            if node not in depended_on and deps
        ]
        for node in to_remove:
            del result[node]
        if not to_remove:
            break
    return result
