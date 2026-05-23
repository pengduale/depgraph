"""Assigns colors to graph nodes based on module grouping or metrics."""

from __future__ import annotations

from typing import Dict, Optional

# Palette for up to 10 distinct module prefixes
_PALETTE = [
    "#4e79a7",
    "#f28e2b",
    "#e15759",
    "#76b7b2",
    "#59a14f",
    "#edc948",
    "#b07aa1",
    "#ff9da7",
    "#9c755f",
    "#bab0ac",
]

_DEFAULT_COLOR = "#cccccc"
_CYCLE_COLOR = "#e15759"
_ENTRY_COLOR = "#59a14f"


def colorize_by_prefix(
    nodes: list[str],
    separator: str = ".",
) -> Dict[str, str]:
    """Return a mapping of node -> hex color based on top-level package prefix.

    Nodes that share the same first component (before *separator*) receive the
    same color.  Up to ``len(_PALETTE)`` distinct groups are supported; any
    overflow wraps around.
    """
    prefix_index: Dict[str, int] = {}
    result: Dict[str, str] = {}

    for node in nodes:
        prefix = node.split(separator)[0]
        if prefix not in prefix_index:
            prefix_index[prefix] = len(prefix_index)
        idx = prefix_index[prefix] % len(_PALETTE)
        result[node] = _PALETTE[idx]

    return result


def colorize_by_metric(
    nodes: list[str],
    metrics: Dict[str, Dict[str, int]],
    metric_key: str = "in_degree",
) -> Dict[str, str]:
    """Return a mapping of node -> hex color based on a numeric metric.

    Nodes are colored on a white-to-blue gradient proportional to their metric
    value.  Nodes missing from *metrics* are treated as having value 0.
    """
    values = [metrics.get(n, {}).get(metric_key, 0) for n in nodes]
    max_val = max(values, default=1) or 1

    result: Dict[str, str] = {}
    for node, val in zip(nodes, values):
        intensity = int(255 * (1 - val / max_val))  # high value -> darker blue
        r = intensity
        g = intensity
        b = 255
        result[node] = f"#{r:02x}{g:02x}{b:02x}"

    return result


def apply_cycle_color(
    color_map: Dict[str, str],
    cycle_nodes: list[str],
    cycle_color: str = _CYCLE_COLOR,
) -> Dict[str, str]:
    """Override colors for nodes that participate in a cycle."""
    updated = dict(color_map)
    for node in cycle_nodes:
        updated[node] = cycle_color
    return updated
