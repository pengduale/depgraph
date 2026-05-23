"""Annotate graph nodes with metadata labels (e.g. cycle member, entry point, leaf)."""

from __future__ import annotations

from typing import Dict, List, Set

from depgraph.analyzer import find_cycles, find_entry_points

# Annotation label constants
LABEL_CYCLE = "cycle"
LABEL_ENTRY = "entry"
LABEL_LEAF = "leaf"
LABEL_ISOLATED = "isolated"


def _leaf_nodes(graph: Dict[str, List[str]]) -> Set[str]:
    """Return nodes that have no outgoing edges (pure consumers)."""
    return {node for node, deps in graph.items() if not deps}


def _isolated_nodes(graph: Dict[str, List[str]]) -> Set[str]:
    """Return nodes with no edges at all (no imports and not imported)."""
    depended_on: Set[str] = set()
    for deps in graph.values():
        depended_on.update(deps)
    return {node for node, deps in graph.items() if not deps and node not in depended_on}


def annotate_nodes(graph: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Return a mapping of node -> list of annotation labels.

    Labels assigned:
      - 'cycle'     : node participates in at least one cycle
      - 'entry'     : node is an entry point (nothing depends on it)
      - 'leaf'      : node has no outgoing dependencies
      - 'isolated'  : node has no edges whatsoever
    """
    annotations: Dict[str, List[str]] = {node: [] for node in graph}

    # Cycle membership
    cycles = find_cycles(graph)
    cycle_members: Set[str] = set()
    for cycle in cycles:
        cycle_members.update(cycle)
    for node in cycle_members:
        if node in annotations:
            annotations[node].append(LABEL_CYCLE)

    # Entry points
    for node in find_entry_points(graph):
        if node in annotations:
            annotations[node].append(LABEL_ENTRY)

    # Isolated nodes (subset of leaves — annotate first so leaf is skipped)
    isolated = _isolated_nodes(graph)
    for node in isolated:
        if node in annotations:
            annotations[node].append(LABEL_ISOLATED)

    # Leaf nodes (have no deps but *are* depended on by something)
    for node in _leaf_nodes(graph) - isolated:
        if node in annotations:
            annotations[node].append(LABEL_LEAF)

    return annotations


def filter_by_annotation(annotations: Dict[str, List[str]], label: str) -> List[str]:
    """Return sorted list of nodes that carry the given annotation label."""
    return sorted(node for node, labels in annotations.items() if label in labels)
