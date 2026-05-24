"""Extract subgraphs from a dependency graph."""
from __future__ import annotations
from typing import Dict, Set, List, Optional

Graph = Dict[str, List[str]]


def extract_subgraph(graph: Graph, nodes: List[str]) -> Graph:
    """Return a subgraph containing only the specified nodes and edges between them."""
    node_set: Set[str] = set(nodes)
    subgraph: Graph = {}
    for node in nodes:
        if node in graph:
            subgraph[node] = [dep for dep in graph[node] if dep in node_set]
        else:
            subgraph[node] = []
    return subgraph


def neighborhood(graph: Graph, node: str, radius: int = 1) -> Graph:
    """Return a subgraph of all nodes within *radius* hops from *node*."""
    if node not in graph:
        return {}

    visited: Set[str] = set()
    frontier: Set[str] = {node}

    # Build reverse map for incoming edges
    reverse: Graph = {n: [] for n in graph}
    for src, deps in graph.items():
        for dep in deps:
            if dep not in reverse:
                reverse[dep] = []
            reverse[dep].append(src)

    for _ in range(radius):
        next_frontier: Set[str] = set()
        for n in frontier:
            visited.add(n)
            for dep in graph.get(n, []):
                if dep not in visited:
                    next_frontier.add(dep)
            for src in reverse.get(n, []):
                if src not in visited:
                    next_frontier.add(src)
        frontier = next_frontier - visited

    visited.update(frontier)
    return extract_subgraph(graph, list(visited))


def induced_subgraph(graph: Graph, predicate) -> Graph:
    """Return a subgraph keeping only nodes for which predicate(node) is True."""
    nodes = [n for n in graph if predicate(n)]
    return extract_subgraph(graph, nodes)


def merge_graphs(*graphs: Graph) -> Graph:
    """Merge multiple graphs into one, combining edge lists without duplicates."""
    merged: Graph = {}
    for g in graphs:
        for node, deps in g.items():
            if node not in merged:
                merged[node] = []
            for dep in deps:
                if dep not in merged[node]:
                    merged[node].append(dep)
    return merged
