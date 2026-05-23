"""Analyzes dependency graphs to produce metrics and detect issues."""

from __future__ import annotations

from collections import deque
from typing import Dict, List, Set, Tuple


def find_cycles(graph: Dict[str, List[str]]) -> List[List[str]]:
    """Return all cycles in the dependency graph using DFS."""
    cycles: List[List[str]] = []
    visited: Set[str] = set()
    rec_stack: List[str] = []

    def dfs(node: str) -> None:
        visited.add(node)
        rec_stack.append(node)
        for neighbour in graph.get(node, []):
            if neighbour not in visited:
                dfs(neighbour)
            elif neighbour in rec_stack:
                cycle_start = rec_stack.index(neighbour)
                cycles.append(rec_stack[cycle_start:] + [neighbour])
        rec_stack.pop()

    for node in list(graph.keys()):
        if node not in visited:
            dfs(node)

    return cycles


def compute_metrics(graph: Dict[str, List[str]]) -> Dict[str, Dict]:
    """Compute per-node metrics: in-degree, out-degree, and fan-in/fan-out."""
    metrics: Dict[str, Dict] = {node: {"in_degree": 0, "out_degree": 0} for node in graph}

    for node, deps in graph.items():
        metrics[node]["out_degree"] = len(deps)
        for dep in deps:
            if dep in metrics:
                metrics[dep]["in_degree"] += 1

    return metrics


def find_entry_points(graph: Dict[str, List[str]]) -> List[str]:
    """Return nodes with no incoming edges (roots of the dependency tree)."""
    all_deps: Set[str] = set()
    for deps in graph.values():
        all_deps.update(deps)
    return sorted(node for node in graph if node not in all_deps)


def find_most_depended_on(graph: Dict[str, List[str]], top_n: int = 5) -> List[Tuple[str, int]]:
    """Return the top N most depended-on modules (highest in-degree)."""
    metrics = compute_metrics(graph)
    ranked = sorted(metrics.items(), key=lambda x: x[1]["in_degree"], reverse=True)
    return [(node, data["in_degree"]) for node, data in ranked[:top_n]]
