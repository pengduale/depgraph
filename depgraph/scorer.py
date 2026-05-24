"""Scores nodes in a dependency graph based on structural importance."""

from __future__ import annotations

from typing import Dict


def _in_degree(graph: dict[str, list[str]]) -> dict[str, int]:
    """Return the in-degree (number of dependents) for every node."""
    counts: dict[str, int] = {node: 0 for node in graph}
    for deps in graph.values():
        for dep in deps:
            if dep in counts:
                counts[dep] += 1
    return counts


def _out_degree(graph: dict[str, list[str]]) -> dict[str, int]:
    """Return the out-degree (number of dependencies) for every node."""
    return {node: len(deps) for node, deps in graph.items()}


def score_nodes(
    graph: dict[str, list[str]],
    in_weight: float = 0.6,
    out_weight: float = 0.4,
) -> dict[str, float]:
    """Compute an importance score for each node.

    Score = in_weight * normalised_in_degree + out_weight * normalised_out_degree

    Parameters
    ----------
    graph:      adjacency dict {node: [dep, ...]}
    in_weight:  contribution of in-degree to the final score (default 0.6)
    out_weight: contribution of out-degree to the final score (default 0.4)

    Returns
    -------
    dict mapping each node to a float score in [0.0, 1.0].
    """
    if not graph:
        return {}

    in_deg = _in_degree(graph)
    out_deg = _out_degree(graph)

    max_in = max(in_deg.values(), default=1) or 1
    max_out = max(out_deg.values(), default=1) or 1

    scores: dict[str, float] = {}
    for node in graph:
        norm_in = in_deg[node] / max_in
        norm_out = out_deg[node] / max_out
        scores[node] = round(in_weight * norm_in + out_weight * norm_out, 4)

    return scores


def rank_nodes(scores: dict[str, float], top: int | None = None) -> list[tuple[str, float]]:
    """Return nodes sorted by score descending.

    Parameters
    ----------
    scores: output of :func:`score_nodes`
    top:    if given, return only the *top* highest-scoring nodes

    Returns
    -------
    List of (node, score) tuples ordered from highest to lowest score.
    """
    ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
    if top is not None:
        ranked = ranked[:top]
    return ranked


def format_scores(ranked: list[tuple[str, float]]) -> str:
    """Format ranked scores as a human-readable table."""
    if not ranked:
        return "(no nodes)"
    width = max(len(node) for node, _ in ranked)
    lines = [f"{'Node':<{width}}  Score"]
    lines.append("-" * (width + 8))
    for node, score in ranked:
        lines.append(f"{node:<{width}}  {score:.4f}")
    return "\n".join(lines)
