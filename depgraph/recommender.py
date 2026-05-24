"""Suggests refactoring actions based on dependency graph metrics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from depgraph.analyzer import find_cycles, compute_metrics


@dataclass
class Recommendation:
    category: str  # 'cycle', 'high_coupling', 'god_module', 'isolated'
    node: str
    message: str
    severity: str  # 'error', 'warning', 'info'


def recommend_cycles(
    graph: Dict[str, List[str]]
) -> List[Recommendation]:
    """Flag every node that participates in a dependency cycle."""
    cycles = find_cycles(graph)
    seen: set[str] = set()
    recs: List[Recommendation] = []
    for cycle in cycles:
        for node in cycle:
            if node not in seen:
                seen.add(node)
                recs.append(
                    Recommendation(
                        category="cycle",
                        node=node,
                        message=f"{node!r} participates in a dependency cycle.",
                        severity="error",
                    )
                )
    return recs


def recommend_high_coupling(
    graph: Dict[str, List[str]],
    threshold: int = 5,
) -> List[Recommendation]:
    """Flag nodes whose out-degree exceeds *threshold*."""
    metrics = compute_metrics(graph)
    recs: List[Recommendation] = []
    for node, m in metrics.items():
        if m["out_degree"] > threshold:
            recs.append(
                Recommendation(
                    category="high_coupling",
                    node=node,
                    message=(
                        f"{node!r} imports {m['out_degree']} modules "
                        f"(threshold: {threshold})."
                    ),
                    severity="warning",
                )
            )
    return recs


def recommend_god_modules(
    graph: Dict[str, List[str]],
    threshold: int = 5,
) -> List[Recommendation]:
    """Flag nodes that are depended upon by many others (high in-degree)."""
    metrics = compute_metrics(graph)
    recs: List[Recommendation] = []
    for node, m in metrics.items():
        if m["in_degree"] > threshold:
            recs.append(
                Recommendation(
                    category="god_module",
                    node=node,
                    message=(
                        f"{node!r} is imported by {m['in_degree']} modules "
                        f"(threshold: {threshold})."
                    ),
                    severity="warning",
                )
            )
    return recs


def recommend_isolated(
    graph: Dict[str, List[str]]
) -> List[Recommendation]:
    """Flag nodes with no imports and no dependents."""
    metrics = compute_metrics(graph)
    recs: List[Recommendation] = []
    for node, m in metrics.items():
        if m["in_degree"] == 0 and m["out_degree"] == 0:
            recs.append(
                Recommendation(
                    category="isolated",
                    node=node,
                    message=f"{node!r} is isolated (no imports, no dependents).",
                    severity="info",
                )
            )
    return recs


def get_recommendations(
    graph: Dict[str, List[str]],
    coupling_threshold: int = 5,
    god_threshold: int = 5,
) -> List[Recommendation]:
    """Run all recommendation checks and return combined list."""
    recs: List[Recommendation] = []
    recs.extend(recommend_cycles(graph))
    recs.extend(recommend_high_coupling(graph, coupling_threshold))
    recs.extend(recommend_god_modules(graph, god_threshold))
    recs.extend(recommend_isolated(graph))
    return recs


def format_recommendations(recs: List[Recommendation]) -> str:
    """Render recommendations as a human-readable string."""
    if not recs:
        return "No recommendations — graph looks healthy."
    lines: List[str] = []
    for r in recs:
        tag = r.severity.upper().ljust(7)
        lines.append(f"[{tag}] ({r.category}) {r.message}")
    return "\n".join(lines)
