"""Assigns weights to edges based on various graph metrics."""

from __future__ import annotations

from typing import Dict, Tuple

Graph = Dict[str, list[str]]
EdgeWeights = Dict[Tuple[str, str], float]


def _in_degree(graph: Graph) -> Dict[str, int]:
    counts: Dict[str, int] = {n: 0 for n in graph}
    for deps in graph.values():
        for dep in deps:
            if dep in counts:
                counts[dep] += 1
    return counts


def weight_by_shared_dependents(graph: Graph) -> EdgeWeights:
    """Weight each edge (u -> v) by the number of nodes that also depend on v."""
    in_deg = _in_degree(graph)
    weights: EdgeWeights = {}
    for node, deps in graph.items():
        for dep in deps:
            weights[(node, dep)] = float(in_deg.get(dep, 0))
    return weights


def weight_by_out_degree(graph: Graph) -> EdgeWeights:
    """Weight each edge (u -> v) by the out-degree of the source node u."""
    weights: EdgeWeights = {}
    for node, deps in graph.items():
        out = float(len(deps))
        for dep in deps:
            weights[(node, dep)] = out
    return weights


def weight_by_combined(graph: Graph, alpha: float = 0.5) -> EdgeWeights:
    """Blend shared-dependents and out-degree weights with factor alpha."""
    if not 0.0 <= alpha <= 1.0:
        raise ValueError("alpha must be between 0.0 and 1.0")
    shared = weight_by_shared_dependents(graph)
    out_deg = weight_by_out_degree(graph)
    all_edges = set(shared) | set(out_deg)
    return {
        edge: alpha * shared.get(edge, 0.0) + (1.0 - alpha) * out_deg.get(edge, 0.0)
        for edge in all_edges
    }


def normalize_weights(weights: EdgeWeights) -> EdgeWeights:
    """Normalize weights to the [0.0, 1.0] range."""
    if not weights:
        return {}
    max_w = max(weights.values())
    if max_w == 0.0:
        return {edge: 0.0 for edge in weights}
    return {edge: w / max_w for edge, w in weights.items()}


def format_weights(weights: EdgeWeights, top_n: int = 10) -> str:
    """Return a human-readable summary of the heaviest edges."""
    sorted_edges = sorted(weights.items(), key=lambda kv: kv[1], reverse=True)
    lines = ["Edge Weights (top {})".format(min(top_n, len(sorted_edges))), "-" * 40]
    for (src, dst), w in sorted_edges[:top_n]:
        lines.append(f"  {src} -> {dst}  {w:.4f}")
    return "\n".join(lines)
