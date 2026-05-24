"""CLI command: show topological order or layer assignments."""

import argparse
import json
import sys

from depgraph.parser import build_dependency_graph
from depgraph.cli import collect_python_files
from depgraph.topo import topological_sort, assign_layers, layers_to_groups


def parse_topo_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="depgraph-topo",
        description="Show topological order or layer assignments for a project.",
    )
    parser.add_argument("path", help="File or directory to analyse")
    parser.add_argument(
        "--mode",
        choices=["order", "layers"],
        default="order",
        help="'order' prints a flat sorted list; 'layers' groups nodes by depth",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
        help="Output format",
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_topo_args(argv)

    files = collect_python_files(args.path)
    graph = build_dependency_graph(files)

    if args.mode == "order":
        result = topological_sort(graph)
        if result is None:
            print("ERROR: cycle detected — topological sort not possible.", file=sys.stderr)
            return 1
        if args.fmt == "json":
            print(json.dumps(result, indent=2))
        else:
            for node in result:
                print(node)

    else:  # layers
        layer_map = assign_layers(graph)
        if layer_map is None:
            print("ERROR: cycle detected — layer assignment not possible.", file=sys.stderr)
            return 1
        groups = layers_to_groups(layer_map)
        if args.fmt == "json":
            print(json.dumps({str(k): v for k, v in groups.items()}, indent=2))
        else:
            for lvl, nodes in groups.items():
                print(f"Layer {lvl}: {', '.join(nodes)}")

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
