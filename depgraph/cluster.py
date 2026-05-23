"""Cluster nodes into logical groups for rendering and analysis."""

from __future__ import annotations
from typing import Dict, List, Set, Tuple


def cluster_by_prefix(nodes: List[str], depth: int = 1) -> Dict[str, List[str]]:
    """Group nodes into clusters based on their dotted-prefix at the given depth.

    Args:
        nodes: List of module names.
        depth: Number of prefix parts to use as cluster key.

    Returns:
        Mapping from cluster label to list of member nodes.
    """
    clusters: Dict[str, List[str]] = {}
    for node in nodes:
        parts = node.split(".")
        key = ".".join(parts[:depth]) if len(parts) >= depth else node
        clusters.setdefault(key, []).append(node)
    return clusters


def merge_small_clusters(
    clusters: Dict[str, List[str]], min_size: int = 2
) -> Dict[str, List[str]]:
    """Merge clusters smaller than *min_size* into an "other" bucket.

    Args:
        clusters: Existing cluster mapping.
        min_size: Minimum number of members to keep a cluster separate.

    Returns:
        New cluster mapping with small clusters merged under "other".
    """
    result: Dict[str, List[str]] = {}
    other: List[str] = []
    for label, members in clusters.items():
        if len(members) >= min_size:
            result[label] = list(members)
        else:
            other.extend(members)
    if other:
        result["other"] = other
    return result


def intra_cluster_edges(
    graph: Dict[str, List[str]], clusters: Dict[str, List[str]]
) -> Dict[str, List[Tuple[str, str]]]:
    """Return edges that stay within the same cluster.

    Args:
        graph: Dependency graph {node: [dependency, ...]}.
        clusters: Cluster mapping from cluster_by_prefix or similar.

    Returns:
        Mapping from cluster label to list of (src, dst) edge tuples.
    """
    node_to_cluster: Dict[str, str] = {}
    for label, members in clusters.items():
        for m in members:
            node_to_cluster[m] = label

    result: Dict[str, List[Tuple[str, str]]] = {label: [] for label in clusters}
    for src, deps in graph.items():
        src_cluster = node_to_cluster.get(src)
        if src_cluster is None:
            continue
        for dst in deps:
            if node_to_cluster.get(dst) == src_cluster:
                result[src_cluster].append((src, dst))
    return result


def cluster_summary(clusters: Dict[str, List[str]]) -> List[Dict]:
    """Return a sorted summary list for reporting."""
    return sorted(
        [{"cluster": label, "size": len(members), "members": sorted(members)}
         for label, members in clusters.items()],
        key=lambda x: (-x["size"], x["cluster"]),
    )
