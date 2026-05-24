"""Formats dependency graphs as human-readable text tables."""

from __future__ import annotations

from typing import Dict, List, Set

Graph = Dict[str, List[str]]


def format_adjacency_list(graph: Graph) -> str:
    """Return a sorted adjacency-list text representation."""
    lines: List[str] = []
    for node in sorted(graph):
        deps = sorted(graph[node])
        dep_str = ", ".join(deps) if deps else "(none)"
        lines.append(f"  {node} -> {dep_str}")
    return "Adjacency list:\n" + "\n".join(lines) if lines else "Adjacency list: (empty graph)"


def format_edge_list(graph: Graph) -> str:
    """Return a sorted edge-list text representation."""
    edges: List[str] = []
    for node in sorted(graph):
        for dep in sorted(graph[node]):
            edges.append(f"  {node} -> {dep}")
    if not edges:
        return "Edge list: (no edges)"
    return "Edge list:\n" + "\n".join(edges)


def format_table(graph: Graph) -> str:
    """Return a padded two-column table of edges."""
    rows: List[tuple[str, str]] = []
    for node in sorted(graph):
        for dep in sorted(graph[node]):
            rows.append((node, dep))
    if not rows:
        return "No edges to display."
    col1 = max(len(r[0]) for r in rows)
    col2 = max(len(r[1]) for r in rows)
    header = f"  {'Source':<{col1}}  {'Target':<{col2}}"
    sep = "  " + "-" * col1 + "  " + "-" * col2
    body = "\n".join(f"  {src:<{col1}}  {tgt:<{col2}}" for src, tgt in rows)
    return "\n".join([header, sep, body])


def format_graph(graph: Graph, style: str = "adjacency") -> str:
    """Dispatch to a named formatter.

    Supported styles: ``adjacency``, ``edges``, ``table``.
    """
    styles = {
        "adjacency": format_adjacency_list,
        "edges": format_edge_list,
        "table": format_table,
    }
    if style not in styles:
        raise ValueError(f"Unknown format style {style!r}. Choose from: {list(styles)}.")
    return styles[style](graph)
