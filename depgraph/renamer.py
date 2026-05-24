"""Rename nodes in a dependency graph, updating all edges accordingly."""

from __future__ import annotations

from typing import Dict, Optional


Graph = Dict[str, list[str]]


def rename_node(graph: Graph, old_name: str, new_name: str) -> Graph:
    """Return a new graph with *old_name* replaced by *new_name* everywhere.

    Raises ValueError if *new_name* already exists in the graph.
    """
    if old_name not in graph:
        return {k: list(v) for k, v in graph.items()}
    if new_name in graph and new_name != old_name:
        raise ValueError(f"Node '{new_name}' already exists in the graph.")

    result: Graph = {}
    for node, deps in graph.items():
        key = new_name if node == old_name else node
        result[key] = [
            new_name if dep == old_name else dep for dep in deps
        ]
    return result


def rename_nodes(graph: Graph, mapping: Dict[str, str]) -> Graph:
    """Apply multiple renames described by *mapping* {old: new}.

    Renames are applied sequentially; later renames see the result of
    earlier ones.  Raises ValueError on conflicts.
    """
    current = {k: list(v) for k, v in graph.items()}
    for old, new in mapping.items():
        current = rename_node(current, old, new)
    return current


def normalize_names(
    graph: Graph,
    transform: Optional[callable] = None,  # type: ignore[type-arg]
) -> Graph:
    """Rename every node by applying *transform* (default: str.lower).

    Raises ValueError if the transformation produces duplicate node names.
    """
    if transform is None:
        transform = str.lower

    mapping: Dict[str, str] = {}
    seen: Dict[str, str] = {}
    for node in graph:
        new_name = transform(node)
        if new_name in seen and seen[new_name] != node:
            raise ValueError(
                f"Normalization collision: '{node}' and '{seen[new_name]}' "
                f"both map to '{new_name}'."
            )
        seen[new_name] = node
        mapping[node] = new_name

    return rename_nodes(graph, mapping)


def format_rename_diff(old_graph: Graph, new_graph: Graph) -> str:
    """Return a human-readable summary of nodes that changed names."""
    old_nodes = set(old_graph)
    new_nodes = set(new_graph)
    added = new_nodes - old_nodes
    removed = old_nodes - new_nodes
    lines = []
    for node in sorted(removed):
        lines.append(f"  - {node}")
    for node in sorted(added):
        lines.append(f"  + {node}")
    if not lines:
        return "No node renames detected."
    return "Node renames:\n" + "\n".join(lines)
