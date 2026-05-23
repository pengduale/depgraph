"""SVG rendering helpers for clustered dependency graphs."""

from __future__ import annotations

from typing import Dict, List, Tuple

_CLUSTER_OPACITY = "0.12"
_CLUSTER_STROKE = "#888"
_PADDING = 20
_NODE_W = 120
_NODE_H = 36


def _cluster_bbox(
    members: List[str],
    positions: Dict[str, Tuple[float, float]],
) -> Tuple[float, float, float, float]:
    """Return (x, y, width, height) bounding box for a cluster."""
    xs = [positions[m][0] for m in members if m in positions]
    ys = [positions[m][1] for m in members if m in positions]
    if not xs:
        return (0.0, 0.0, 0.0, 0.0)
    x = min(xs) - _PADDING
    y = min(ys) - _PADDING
    w = max(xs) - min(xs) + _NODE_W + _PADDING * 2
    h = max(ys) - min(ys) + _NODE_H + _PADDING * 2
    return (x, y, w, h)


def render_cluster_backgrounds(
    clusters: Dict[str, List[str]],
    positions: Dict[str, Tuple[float, float]],
    colors: Dict[str, str],
) -> str:
    """Return SVG markup for translucent cluster background rectangles.

    Args:
        clusters: Mapping from cluster label to member node names.
        positions: Mapping from node name to (x, y) top-left position.
        colors: Mapping from cluster label to fill colour (hex or named).

    Returns:
        SVG string containing <g> elements for each cluster background.
    """
    parts: List[str] = []
    for label, members in clusters.items():
        x, y, w, h = _cluster_bbox(members, positions)
        if w == 0 and h == 0:
            continue
        color = colors.get(label, "#cccccc")
        parts.append(
            f'<g class="cluster" data-label="{label}">'
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="8" ry="8" fill="{color}" fill-opacity="{_CLUSTER_OPACITY}" '
            f'stroke="{_CLUSTER_STROKE}" stroke-width="1" stroke-dasharray="4 2"/>'
            f'<text x="{x + 6:.1f}" y="{y + 14:.1f}" '
            f'font-size="11" fill="{_CLUSTER_STROKE}" font-style="italic">'
            f'{label}</text>'
            f'</g>'
        )
    return "\n".join(parts)


def default_cluster_colors(clusters: Dict[str, List[str]]) -> Dict[str, str]:
    """Assign a simple cycling palette to clusters.

    Args:
        clusters: Cluster mapping whose keys are used for colour assignment.

    Returns:
        Mapping from cluster label to hex colour string.
    """
    palette = [
        "#4e79a7", "#f28e2b", "#e15759", "#76b7b2",
        "#59a14f", "#edc948", "#b07aa1", "#ff9da7",
    ]
    return {
        label: palette[i % len(palette)]
        for i, label in enumerate(sorted(clusters))
    }
