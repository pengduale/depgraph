"""Node and edge inspection utilities for depgraph."""
from __future__ import annotations

from typing import Dict, List, Tuple

Graph = Dict[str, List[str]]


def inspect_node(graph: Graph, node: str) -> Dict:
    """Return detailed information about a single node."""
    if node not in graph:
        return {"error": f"Node '{node}' not found in graph"}

    deps = graph[node]
    in_edges = [src for src, targets in graph.items() if node in targets]

    return {
        "node": node,
        "out_degree": len(deps),
        "in_degree": len(in_edges),
        "dependencies": sorted(deps),
        "dependents": sorted(in_edges),
        "is_root": len(in_edges) == 0,
        "is_leaf": len(deps) == 0,
        "is_isolated": len(in_edges) == 0 and len(deps) == 0,
    }


def inspect_edge(graph: Graph, src: str, dst: str) -> Dict:
    """Return information about a directed edge."""
    src_exists = src in graph
    dst_exists = dst in graph
    edge_exists = src_exists and dst in graph[src]

    return {
        "src": src,
        "dst": dst,
        "exists": edge_exists,
        "src_exists": src_exists,
        "dst_exists": dst_exists,
    }


def inspect_all_nodes(graph: Graph) -> List[Dict]:
    """Return inspection data for every node in the graph."""
    return [inspect_node(graph, node) for node in sorted(graph)]


def find_bottlenecks(graph: Graph, threshold: int = 2) -> List[str]:
    """Return nodes whose in-degree meets or exceeds *threshold*."""
    result = []
    for node in sorted(graph):
        info = inspect_node(graph, node)
        if info.get("in_degree", 0) >= threshold:
            result.append(node)
    return result


def format_node_report(info: Dict) -> str:
    """Format a single node inspection dict as a human-readable string."""
    if "error" in info:
        return info["error"]
    lines = [
        f"Node     : {info['node']}",
        f"In-degree: {info['in_degree']}",
        f"Out-degree: {info['out_degree']}",
        f"Dependencies : {', '.join(info['dependencies']) or 'none'}",
        f"Dependents   : {', '.join(info['dependents']) or 'none'}",
        f"Root: {info['is_root']}  Leaf: {info['is_leaf']}  Isolated: {info['is_isolated']}",
    ]
    return "\n".join(lines)
