"""Compare two dependency graphs and produce a structured comparison report."""

from __future__ import annotations

from typing import Dict, List, Tuple

Graph = Dict[str, List[str]]


def added_nodes(old: Graph, new: Graph) -> List[str]:
    """Return nodes present in *new* but not in *old*."""
    return sorted(set(new) - set(old))


def removed_nodes(old: Graph, new: Graph) -> List[str]:
    """Return nodes present in *old* but not in *new*."""
    return sorted(set(old) - set(new))


def added_edges(old: Graph, new: Graph) -> List[Tuple[str, str]]:
    """Return (src, dst) pairs present in *new* but not in *old*."""
    old_edges = _edge_set(old)
    new_edges = _edge_set(new)
    return sorted(new_edges - old_edges)


def removed_edges(old: Graph, new: Graph) -> List[Tuple[str, str]]:
    """Return (src, dst) pairs present in *old* but not in *new*."""
    old_edges = _edge_set(old)
    new_edges = _edge_set(new)
    return sorted(old_edges - new_edges)


def compare_graphs(old: Graph, new: Graph) -> Dict[str, object]:
    """Return a full comparison dict between *old* and *new* graphs."""
    return {
        "added_nodes": added_nodes(old, new),
        "removed_nodes": removed_nodes(old, new),
        "added_edges": added_edges(old, new),
        "removed_edges": removed_edges(old, new),
    }


def is_identical(old: Graph, new: Graph) -> bool:
    """Return True when both graphs have the same nodes and edges."""
    result = compare_graphs(old, new)
    return all(len(v) == 0 for v in result.values())


def format_comparison(comparison: Dict[str, object]) -> str:
    """Render a human-readable summary of a comparison dict."""
    lines: List[str] = []
    for label, key in [
        ("Added nodes", "added_nodes"),
        ("Removed nodes", "removed_nodes"),
        ("Added edges", "added_edges"),
        ("Removed edges", "removed_edges"),
    ]:
        items = comparison[key]
        lines.append(f"{label}: {len(items)}")
        for item in items:
            if isinstance(item, tuple):
                lines.append(f"  {item[0]} -> {item[1]}")
            else:
                lines.append(f"  {item}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _edge_set(graph: Graph) -> set:
    edges = set()
    for src, deps in graph.items():
        for dst in deps:
            edges.add((src, dst))
    return edges
