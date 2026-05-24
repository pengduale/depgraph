"""Summarizes a dependency graph into a human-readable or structured report."""

from __future__ import annotations

from typing import Dict, List

from depgraph.analyzer import compute_metrics, find_cycles, find_entry_points, find_most_depended_on


def summarize(graph: Dict[str, List[str]]) -> Dict:
    """Return a structured summary dict for the given dependency graph."""
    metrics = compute_metrics(graph)
    cycles = find_cycles(graph)
    entry_points = find_entry_points(graph)
    most_depended = find_most_depended_on(graph, top_n=5)

    total_nodes = len(graph)
    total_edges = sum(len(deps) for deps in graph.values())
    avg_out = total_edges / total_nodes if total_nodes else 0.0
    max_in_node, max_in_val = max(
        ((n, metrics[n]["in_degree"]) for n in metrics),
        key=lambda t: t[1],
        default=(None, 0),
    )

    return {
        "total_nodes": total_nodes,
        "total_edges": total_edges,
        "average_out_degree": round(avg_out, 3),
        "entry_points": sorted(entry_points),
        "most_depended_on": most_depended,
        "cycles_detected": len(cycles) > 0,
        "cycle_count": len(cycles),
        "cycles": cycles,
        "most_imported_node": max_in_node,
        "most_imported_count": max_in_val,
    }


def format_summary(summary: Dict) -> str:
    """Format a summary dict as a printable string."""
    lines: List[str] = []
    lines.append("=== Dependency Graph Summary ===")
    lines.append(f"Nodes          : {summary['total_nodes']}")
    lines.append(f"Edges          : {summary['total_edges']}")
    lines.append(f"Avg out-degree : {summary['average_out_degree']}")

    eps = ", ".join(summary["entry_points"]) or "(none)"
    lines.append(f"Entry points   : {eps}")

    if summary["most_imported_node"]:
        lines.append(
            f"Most imported  : {summary['most_imported_node']} "
            f"({summary['most_imported_count']} times)"
        )

    lines.append(f"Cycles         : {'YES' if summary['cycles_detected'] else 'no'} "
                 f"({summary['cycle_count']} cycle(s))")

    if summary["most_depended_on"]:
        top = ", ".join(f"{n}({c})" for n, c in summary["most_depended_on"])
        lines.append(f"Top depended-on: {top}")

    return "\n".join(lines)
