"""Trim dependency graphs by removing nodes below a minimum edge threshold."""

from __future__ import annotations

from typing import Dict, List, Set

Graph = Dict[str, List[str]]


def _in_degree(graph: Graph) -> Dict[str, int]:
    """Compute in-degree for every node in the graph."""
    counts: Dict[str, int] = {node: 0 for node in graph}
    for deps in graph.values():
        for dep in deps:
            if dep in counts:
                counts[dep] += 1
    return counts


def _out_degree(graph: Graph) -> Dict[str, int]:
    """Compute out-degree (number of dependencies) for every node."""
    return {node: len(deps) for node, deps in graph.items()}


def trim_by_in_degree(graph: Graph, min_in: int) -> Graph:
    """Remove nodes whose in-degree is strictly below *min_in*.

    Edges pointing to removed nodes are also dropped.
    """
    in_deg = _in_degree(graph)
    keep: Set[str] = {node for node, deg in in_deg.items() if deg >= min_in}
    return {
        node: [d for d in deps if d in keep]
        for node, deps in graph.items()
        if node in keep
    }


def trim_by_out_degree(graph: Graph, min_out: int) -> Graph:
    """Remove nodes whose out-degree is strictly below *min_out*.

    Edges pointing to removed nodes are also dropped.
    """
    out_deg = _out_degree(graph)
    keep: Set[str] = {node for node, deg in out_deg.items() if deg >= min_out}
    return {
        node: [d for d in deps if d in keep]
        for node, deps in graph.items()
        if node in keep
    }


def trim_by_total_degree(graph: Graph, min_total: int) -> Graph:
    """Remove nodes whose combined in+out degree is below *min_total*."""
    in_deg = _in_degree(graph)
    out_deg = _out_degree(graph)
    keep: Set[str] = {
        node
        for node in graph
        if in_deg.get(node, 0) + out_deg.get(node, 0) >= min_total
    }
    return {
        node: [d for d in deps if d in keep]
        for node, deps in graph.items()
        if node in keep
    }


def format_trimmed(original: Graph, trimmed: Graph) -> str:
    """Return a human-readable summary of what was removed."""
    removed = sorted(set(original) - set(trimmed))
    orig_edges = sum(len(v) for v in original.values())
    new_edges = sum(len(v) for v in trimmed.values())
    lines = [
        f"Nodes : {len(original)} -> {len(trimmed)} (removed {len(removed)})",
        f"Edges : {orig_edges} -> {new_edges} (removed {orig_edges - new_edges})",
    ]
    if removed:
        lines.append("Removed nodes: " + ", ".join(removed))
    return "\n".join(lines)
