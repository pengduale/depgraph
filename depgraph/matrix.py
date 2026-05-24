"""Adjacency matrix representation of a dependency graph."""

from __future__ import annotations
from typing import Dict, List, Tuple


def build_matrix(
    graph: Dict[str, List[str]]
) -> Tuple[List[str], List[List[int]]]:
    """Return (nodes, matrix) where matrix[i][j]==1 means node i imports node j."""
    nodes = sorted(graph.keys())
    index = {n: i for i, n in enumerate(nodes)}
    size = len(nodes)
    matrix: List[List[int]] = [[0] * size for _ in range(size)]
    for src, deps in graph.items():
        i = index[src]
        for dep in deps:
            if dep in index:
                matrix[i][index[dep]] = 1
    return nodes, matrix


def matrix_to_graph(nodes: List[str], matrix: List[List[int]]) -> Dict[str, List[str]]:
    """Reconstruct a dependency graph from an adjacency matrix."""
    graph: Dict[str, List[str]] = {n: [] for n in nodes}
    for i, src in enumerate(nodes):
        for j, dst in enumerate(nodes):
            if matrix[i][j]:
                graph[src].append(dst)
    return graph


def format_matrix(nodes: List[str], matrix: List[List[int]]) -> str:
    """Render the matrix as a plain-text table."""
    if not nodes:
        return "(empty)"
    col_w = max(len(n) for n in nodes)
    row_w = max(len(n) for n in nodes)
    header = " " * (row_w + 2) + "  ".join(n.ljust(col_w) for n in nodes)
    lines = [header]
    for i, src in enumerate(nodes):
        row_vals = "  ".join(str(matrix[i][j]).ljust(col_w) for j in range(len(nodes)))
        lines.append(f"{src.ljust(row_w)}  {row_vals}")
    return "\n".join(lines)


def density(matrix: List[List[int]]) -> float:
    """Return edge density: actual edges / possible edges (excluding self-loops)."""
    n = len(matrix)
    if n <= 1:
        return 0.0
    total = sum(matrix[i][j] for i in range(n) for j in range(n) if i != j)
    possible = n * (n - 1)
    return total / possible
