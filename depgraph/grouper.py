"""Groups nodes in a dependency graph by package prefix or custom mapping."""

from collections import defaultdict
from typing import Dict, List, Optional, Set


def group_by_prefix(nodes: List[str], depth: int = 1) -> Dict[str, List[str]]:
    """Group nodes by their top-level package prefix up to `depth` components.

    Args:
        nodes: List of module names (e.g. ['a.b', 'a.c', 'b.d']).
        depth: How many dot-separated components to use as the group key.

    Returns:
        A dict mapping group key -> list of nodes in that group.
    """
    groups: Dict[str, List[str]] = defaultdict(list)
    for node in nodes:
        parts = node.split(".")
        key = ".".join(parts[:depth])
        groups[key].append(node)
    return dict(groups)


def group_by_mapping(nodes: List[str], mapping: Dict[str, str]) -> Dict[str, List[str]]:
    """Group nodes using an explicit node->group mapping.

    Nodes not present in `mapping` are placed in the '__ungrouped__' group.

    Args:
        nodes: List of module names.
        mapping: Dict of node name -> group name.

    Returns:
        A dict mapping group name -> list of nodes.
    """
    groups: Dict[str, List[str]] = defaultdict(list)
    for node in nodes:
        group = mapping.get(node, "__ungrouped__")
        groups[group].append(node)
    return dict(groups)


def inter_group_edges(
    graph: Dict[str, List[str]],
    groups: Dict[str, List[str]],
) -> List[tuple]:
    """Return edges that cross group boundaries.

    Args:
        graph: Adjacency dict {node: [dependency, ...]}.
        groups: Output of group_by_prefix or group_by_mapping.

    Returns:
        List of (src_group, dst_group) tuples (unique pairs).
    """
    node_to_group: Dict[str, str] = {}
    for group, members in groups.items():
        for member in members:
            node_to_group[member] = group

    seen: Set[tuple] = set()
    result: List[tuple] = []
    for src, deps in graph.items():
        src_group = node_to_group.get(src)
        if src_group is None:
            continue
        for dst in deps:
            dst_group = node_to_group.get(dst)
            if dst_group is None or dst_group == src_group:
                continue
            edge = (src_group, dst_group)
            if edge not in seen:
                seen.add(edge)
                result.append(edge)
    return result
