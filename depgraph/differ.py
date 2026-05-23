"""Computes differences between two dependency graphs."""

from typing import Dict, Set, Tuple

Graph = Dict[str, Set[str]]


def diff_graphs(old: Graph, new: Graph) -> Dict[str, list]:
    """Return added/removed nodes and edges between two dependency graphs.

    Args:
        old: Previous dependency graph mapping module -> set of imports.
        new: Current dependency graph mapping module -> set of imports.

    Returns:
        A dict with keys:
            'added_nodes'   - nodes present in new but not old
            'removed_nodes' - nodes present in old but not new
            'added_edges'   - (src, dst) pairs added
            'removed_edges' - (src, dst) pairs removed
    """
    old_nodes: Set[str] = set(old.keys())
    new_nodes: Set[str] = set(new.keys())

    added_nodes = sorted(new_nodes - old_nodes)
    removed_nodes = sorted(old_nodes - new_nodes)

    old_edges = _edges(old)
    new_edges = _edges(new)

    added_edges = sorted(new_edges - old_edges)
    removed_edges = sorted(old_edges - new_edges)

    return {
        "added_nodes": added_nodes,
        "removed_nodes": removed_nodes,
        "added_edges": added_edges,
        "removed_edges": removed_edges,
    }


def _edges(graph: Graph) -> Set[Tuple[str, str]]:
    """Flatten a graph dict into a set of (src, dst) edge tuples."""
    result: Set[Tuple[str, str]] = set()
    for src, dsts in graph.items():
        for dst in dsts:
            result.add((src, dst))
    return result


def is_empty_diff(diff: Dict[str, list]) -> bool:
    """Return True when the diff contains no changes at all."""
    return not any(diff.get(k) for k in
                   ("added_nodes", "removed_nodes", "added_edges", "removed_edges"))


def format_diff(diff: Dict[str, list]) -> str:
    """Produce a human-readable summary of a graph diff."""
    lines = []
    if diff["added_nodes"]:
        lines.append("Added nodes:")
        lines.extend(f"  + {n}" for n in diff["added_nodes"])
    if diff["removed_nodes"]:
        lines.append("Removed nodes:")
        lines.extend(f"  - {n}" for n in diff["removed_nodes"])
    if diff["added_edges"]:
        lines.append("Added edges:")
        lines.extend(f"  + {s} -> {d}" for s, d in diff["added_edges"])
    if diff["removed_edges"]:
        lines.append("Removed edges:")
        lines.extend(f"  - {s} -> {d}" for s, d in diff["removed_edges"])
    if not lines:
        return "No changes detected."
    return "\n".join(lines)
