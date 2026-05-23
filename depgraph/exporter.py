"""Export dependency graph data to various formats (JSON, DOT)."""

import json
from typing import Dict, Set


def export_json(graph: Dict[str, Set[str]], indent: int = 2) -> str:
    """Export dependency graph as a JSON string.

    Args:
        graph: Mapping of module names to sets of their dependencies.
        indent: JSON indentation level.

    Returns:
        JSON-formatted string representation of the graph.
    """
    serializable = {module: sorted(deps) for module, deps in sorted(graph.items())}
    return json.dumps(serializable, indent=indent)


def export_dot(graph: Dict[str, Set[str]], graph_name: str = "dependencies") -> str:
    """Export dependency graph in Graphviz DOT format.

    Args:
        graph: Mapping of module names to sets of their dependencies.
        graph_name: Name for the DOT digraph.

    Returns:
        DOT-formatted string representation of the graph.
    """
    lines = [f'digraph "{graph_name}" {{', '    rankdir=LR;', '    node [shape=box, style=filled, fillcolor=lightblue];']

    all_nodes: Set[str] = set()
    for module, deps in graph.items():
        all_nodes.add(module)
        all_nodes.update(deps)

    for node in sorted(all_nodes):
        label = node.replace('"', '\\"')
        lines.append(f'    "{label}";')

    lines.append('')
    for module in sorted(graph.keys()):
        for dep in sorted(graph[module]):
            src = module.replace('"', '\\"')
            dst = dep.replace('"', '\\"')
            lines.append(f'    "{src}" -> "{dst}";')

    lines.append('}')
    return '\n'.join(lines)


def save_export(content: str, output_path: str) -> None:
    """Write exported content to a file.

    Args:
        content: String content to write.
        output_path: Destination file path.
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
