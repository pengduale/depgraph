"""Compute and format summary statistics for a dependency graph."""

from __future__ import annotations

from typing import Dict, Any


def compute_stats(graph: Dict[str, list]) -> Dict[str, Any]:
    """Return a dictionary of summary statistics for *graph*.

    Parameters
    ----------
    graph:
        Mapping of module name -> list of imported module names.

    Returns
    -------
    dict with keys:
        node_count, edge_count, avg_out_degree, avg_in_degree,
        max_out_degree, max_in_degree, isolated_count, density
    """
    if not graph:
        return {
            "node_count": 0,
            "edge_count": 0,
            "avg_out_degree": 0.0,
            "avg_in_degree": 0.0,
            "max_out_degree": 0,
            "max_in_degree": 0,
            "isolated_count": 0,
            "density": 0.0,
        }

    node_count = len(graph)

    out_degrees = {node: len(deps) for node, deps in graph.items()}
    edge_count = sum(out_degrees.values())

    in_degrees: Dict[str, int] = {node: 0 for node in graph}
    for deps in graph.values():
        for dep in deps:
            if dep in in_degrees:
                in_degrees[dep] += 1

    avg_out = edge_count / node_count
    avg_in = sum(in_degrees.values()) / node_count

    max_out = max(out_degrees.values(), default=0)
    max_in = max(in_degrees.values(), default=0)

    isolated = sum(
        1 for node in graph
        if out_degrees[node] == 0 and in_degrees[node] == 0
    )

    # Directed density: edges / (n * (n-1))
    possible = node_count * (node_count - 1)
    density = edge_count / possible if possible > 0 else 0.0

    return {
        "node_count": node_count,
        "edge_count": edge_count,
        "avg_out_degree": round(avg_out, 4),
        "avg_in_degree": round(avg_in, 4),
        "max_out_degree": max_out,
        "max_in_degree": max_in,
        "isolated_count": isolated,
        "density": round(density, 6),
    }


def format_stats(stats: Dict[str, Any]) -> str:
    """Return a human-readable string representation of *stats*."""
    lines = [
        "=== Dependency Graph Statistics ===",
        f"  Nodes          : {stats['node_count']}",
        f"  Edges          : {stats['edge_count']}",
        f"  Avg out-degree : {stats['avg_out_degree']}",
        f"  Avg in-degree  : {stats['avg_in_degree']}",
        f"  Max out-degree : {stats['max_out_degree']}",
        f"  Max in-degree  : {stats['max_in_degree']}",
        f"  Isolated nodes : {stats['isolated_count']}",
        f"  Graph density  : {stats['density']}",
    ]
    return "\n".join(lines)
