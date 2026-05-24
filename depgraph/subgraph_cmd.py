"""CLI command for extracting subgraphs."""
from __future__ import annotations

import argparse
import json
import sys

from depgraph.parser import build_dependency_graph
from depgraph.cli import collect_python_files
from depgraph.subgraph import extract_subgraph, neighborhood, induced_subgraph


def parse_subgraph_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="depgraph-subgraph",
        description="Extract a subgraph from a Python project dependency graph.",
    )
    parser.add_argument("path", help="Python file or directory to analyse")
    parser.add_argument(
        "--nodes",
        nargs="+",
        metavar="NODE",
        help="Explicit list of nodes to include in subgraph",
    )
    parser.add_argument(
        "--neighborhood",
        metavar="NODE",
        dest="neighborhood_node",
        help="Extract neighborhood around this node",
    )
    parser.add_argument(
        "--radius",
        type=int,
        default=1,
        help="Hop radius for --neighborhood (default: 1)",
    )
    parser.add_argument(
        "--prefix",
        metavar="PREFIX",
        help="Keep only nodes matching this prefix",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
        help="Output format (default: text)",
    )
    return parser.parse_args(argv)


def main(argv=None) -> None:
    args = parse_subgraph_args(argv)

    files = collect_python_files(args.path)
    graph = build_dependency_graph(files)

    if args.nodes:
        result = extract_subgraph(graph, args.nodes)
    elif args.neighborhood_node:
        result = neighborhood(graph, args.neighborhood_node, radius=args.radius)
    elif args.prefix:
        prefix = args.prefix
        result = induced_subgraph(graph, lambda n: n.startswith(prefix))
    else:
        result = graph

    if args.fmt == "json":
        output = {node: sorted(deps) for node, deps in sorted(result.items())}
        print(json.dumps(output, indent=2))
    else:
        for node in sorted(result):
            deps = sorted(result[node])
            if deps:
                print(f"{node} -> {', '.join(deps)}")
            else:
                print(node)


if __name__ == "__main__":
    main()
