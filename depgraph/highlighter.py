"""Highlight specific nodes and their relationships in the dependency graph."""

from typing import Dict, Set, List, Optional


def highlight_node(
    graph: Dict[str, List[str]],
    node: str,
    include_ancestors: bool = True,
    include_descendants: bool = True,
) -> Dict[str, str]:
    """Return a mapping of node -> highlight class for SVG rendering.

    Classes:
        'focus'      - the target node itself
        'ancestor'   - nodes that depend on the target (upstream)
        'descendant' - nodes the target depends on (downstream)
        'default'    - all other nodes
    """
    if node not in graph:
        raise ValueError(f"Node '{node}' not found in graph.")

    ancestors: Set[str] = set()
    descendants: Set[str] = set()

    if include_ancestors:
        ancestors = _find_ancestors(graph, node)

    if include_descendants:
        descendants = _find_descendants(graph, node)

    highlights: Dict[str, str] = {}
    for n in graph:
        if n == node:
            highlights[n] = "focus"
        elif n in ancestors:
            highlights[n] = "ancestor"
        elif n in descendants:
            highlights[n] = "descendant"
        else:
            highlights[n] = "default"

    return highlights


def _find_ancestors(graph: Dict[str, List[str]], target: str) -> Set[str]:
    """Find all nodes that have a path leading TO the target node."""
    reverse: Dict[str, List[str]] = {n: [] for n in graph}
    for node, deps in graph.items():
        for dep in deps:
            if dep in reverse:
                reverse[dep].append(node)

    visited: Set[str] = set()
    stack = [target]
    while stack:
        current = stack.pop()
        for parent in reverse.get(current, []):
            if parent not in visited:
                visited.add(parent)
                stack.append(parent)
    return visited


def _find_descendants(graph: Dict[str, List[str]], target: str) -> Set[str]:
    """Find all nodes reachable FROM the target node."""
    visited: Set[str] = set()
    stack = list(graph.get(target, []))
    while stack:
        current = stack.pop()
        if current not in visited:
            visited.add(current)
            stack.extend(graph.get(current, []))
    return visited


def get_highlighted_edges(
    graph: Dict[str, List[str]],
    highlights: Dict[str, str],
) -> Dict[tuple, str]:
    """Return edge -> css-class mapping based on highlight state."""
    edge_classes: Dict[tuple, str] = {}
    for src, deps in graph.items():
        for dst in deps:
            src_cls = highlights.get(src, "default")
            dst_cls = highlights.get(dst, "default")
            if "focus" in (src_cls, dst_cls):
                edge_classes[(src, dst)] = "edge-focus"
            elif src_cls != "default" and dst_cls != "default":
                edge_classes[(src, dst)] = "edge-highlighted"
            else:
                edge_classes[(src, dst)] = "edge-default"
    return edge_classes
