"""Generates a human-readable analysis report for a dependency graph."""

from __future__ import annotations

from typing import Dict, List

from depgraph.analyzer import (
    compute_metrics,
    find_cycles,
    find_entry_points,
    find_most_depended_on,
)


def generate_report(graph: Dict[str, List[str]]) -> str:
    """Return a formatted text report summarising the dependency graph."""
    lines: List[str] = []

    lines.append("=" * 50)
    lines.append("Dependency Graph Report")
    lines.append("=" * 50)

    # Summary
    num_nodes = len(graph)
    num_edges = sum(len(deps) for deps in graph.values())
    lines.append(f"\nModules : {num_nodes}")
    lines.append(f"Edges   : {num_edges}")

    # Entry points
    entries = find_entry_points(graph)
    lines.append(f"\nEntry points ({len(entries)}):")
    for ep in entries:
        lines.append(f"  - {ep}")

    # Most depended-on
    top = find_most_depended_on(graph, top_n=5)
    lines.append("\nMost depended-on modules:")
    for module, count in top:
        lines.append(f"  {module}: {count} dependent(s)")

    # Cycles
    cycles = find_cycles(graph)
    if cycles:
        lines.append(f"\n⚠  Circular dependencies detected ({len(cycles)}):")
        for cycle in cycles:
            lines.append("  " + " -> ".join(cycle))
    else:
        lines.append("\n✓  No circular dependencies detected.")

    lines.append("\n" + "=" * 50)
    return "\n".join(lines)


def print_report(graph: Dict[str, List[str]]) -> None:
    """Print the dependency report to stdout."""
    print(generate_report(graph))
