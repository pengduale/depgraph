"""CLI entry-point for graph pruning operations."""

from __future__ import annotations

import argparse
import json
import sys

from depgraph.cli import collect_python_files
from depgraph.parser import build_dependency_graph
from depgraph.pruner import remove_transitive_edges, trim_leaves, trim_roots


def parse_pruner_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="depgraph-prune",
        description="Prune redundant or unwanted nodes/edges from a dependency graph.",
    )
    parser.add_argument(
        "path",
        help="Python file or directory to analyse.",
    )
    parser.add_argument(
        "--transitive",
        action="store_true",
        default=False,
        help="Remove transitive (redundant) edges.",
    )
    parser.add_argument(
        "--trim-leaves",
        dest="trim_leaves",
        type=int,
        metavar="N",
        default=0,
        help="Remove leaf nodes N times (default: 0 = disabled).",
    )
    parser.add_argument(
        "--trim-roots",
        dest="trim_roots",
        type=int,
        metavar="N",
        default=0,
        help="Remove root nodes N times (default: 0 = disabled).",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:  # pragma: no cover
    args = parse_pruner_args(argv)

    files = collect_python_files(args.path)
    graph = build_dependency_graph(files)

    if args.transitive:
        graph = remove_transitive_edges(graph)
    if args.trim_leaves > 0:
        graph = trim_leaves(graph, passes=args.trim_leaves)
    if args.trim_roots > 0:
        graph = trim_roots(graph, passes=args.trim_roots)

    if args.format == "json":
        serialisable = {k: sorted(v) for k, v in graph.items()}
        print(json.dumps(serialisable, indent=2))
    else:
        if not graph:
            print("(empty graph after pruning)")
            return
        for node in sorted(graph):
            deps = sorted(graph[node])
            dep_str = ", ".join(deps) if deps else "(none)"
            print(f"{node} -> {dep_str}")


if __name__ == "__main__":
    main(sys.argv[1:])
