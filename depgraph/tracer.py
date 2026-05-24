"""Trace dependency chains between two nodes in a graph."""

from typing import Dict, List, Optional, Set

Graph = Dict[str, List[str]]


def trace_chain(graph: Graph, source: str, target: str) -> Optional[List[str]]:
    """Return the shortest dependency chain from source to target, or None."""
    if source not in graph:
        return None
    if source == target:
        return [source]
    from collections import deque
    queue = deque([[source]])
    visited: Set[str] = {source}
    while queue:
        path = queue.popleft()
        current = path[-1]
        for dep in graph.get(current, []):
            if dep == target:
                return path + [dep]
            if dep not in visited:
                visited.add(dep)
                queue.append(path + [dep])
    return None


def trace_all_chains(graph: Graph, source: str, target: str) -> List[List[str]]:
    """Return all simple dependency chains from source to target."""
    if source not in graph:
        return []
    if source == target:
        return [[source]]
    results: List[List[str]] = []

    def dfs(current: str, path: List[str], visited: Set[str]) -> None:
        for dep in graph.get(current, []):
            if dep == target:
                results.append(path + [dep])
            elif dep not in visited:
                dfs(dep, path + [dep], visited | {dep})

    dfs(source, [source], {source})
    return results


def format_chain(chain: List[str]) -> str:
    """Format a dependency chain as a human-readable arrow string."""
    return " -> ".join(chain)


def chain_summary(graph: Graph, source: str, target: str) -> Dict:
    """Return a summary dict with shortest and all chains between two nodes."""
    shortest = trace_chain(graph, source, target)
    all_chains = trace_all_chains(graph, source, target)
    return {
        "source": source,
        "target": target,
        "reachable": shortest is not None,
        "shortest": shortest,
        "shortest_length": len(shortest) - 1 if shortest else None,
        "all_chains": all_chains,
        "chain_count": len(all_chains),
    }
