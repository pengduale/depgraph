"""Heatmap: assign heat values to nodes based on a chosen metric for visual intensity."""

from __future__ import annotations

from typing import Dict, List, Tuple


def _in_degree(graph: Dict[str, List[str]]) -> Dict[str, int]:
    counts: Dict[str, int] = {n: 0 for n in graph}
    for deps in graph.values():
        for d in deps:
            if d in counts:
                counts[d] += 1
    return counts


def _out_degree(graph: Dict[str, List[str]]) -> Dict[str, int]:
    return {n: len(deps) for n, deps in graph.items()}


def _total_degree(graph: Dict[str, List[str]]) -> Dict[str, int]:
    ind = _in_degree(graph)
    outd = _out_degree(graph)
    return {n: ind[n] + outd[n] for n in graph}


def compute_heat(
    graph: Dict[str, List[str]],
    metric: str = "in_degree",
) -> Dict[str, float]:
    """Return a 0.0–1.0 heat value for every node.

    metric: 'in_degree' | 'out_degree' | 'total_degree'
    """
    if metric == "in_degree":
        raw = _in_degree(graph)
    elif metric == "out_degree":
        raw = _out_degree(graph)
    elif metric == "total_degree":
        raw = _total_degree(graph)
    else:
        raise ValueError(f"Unknown metric: {metric!r}")

    if not raw:
        return {}

    max_val = max(raw.values()) or 1
    return {n: v / max_val for n, v in raw.items()}


def heat_to_color(heat: float, palette: str = "red") -> str:
    """Map a 0.0–1.0 heat value to an RGB hex colour string.

    palette: 'red' | 'blue' | 'green'
    """
    heat = max(0.0, min(1.0, heat))
    intensity = int(heat * 255)
    low = 220 - int(heat * 180)
    if palette == "red":
        return f"#{intensity:02x}{low:02x}{low:02x}"
    if palette == "blue":
        return f"#{low:02x}{low:02x}{intensity:02x}"
    if palette == "green":
        return f"#{low:02x}{intensity:02x}{low:02x}"
    raise ValueError(f"Unknown palette: {palette!r}")


def build_heatmap(
    graph: Dict[str, List[str]],
    metric: str = "in_degree",
    palette: str = "red",
) -> Dict[str, str]:
    """Return node -> hex colour mapping."""
    heat = compute_heat(graph, metric)
    return {node: heat_to_color(h, palette) for node, h in heat.items()}


def format_heatmap(heat: Dict[str, float]) -> str:
    """Human-readable table of node heat values, sorted descending."""
    if not heat:
        return "(empty graph)"
    rows: List[Tuple[float, str]] = sorted(
        ((v, n) for n, v in heat.items()), reverse=True
    )
    lines = [f"{'Node':<40} Heat", "-" * 47]
    for val, name in rows:
        lines.append(f"{name:<40} {val:.3f}")
    return "\n".join(lines)
