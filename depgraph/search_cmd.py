"""CLI sub-commands for querying / searching the dependency graph."""

from __future__ import annotations

import argparse
import sys
from typing import List

from depgraph.cli import collect_python_files
from depgraph.parser import build_dependency_graph
from depgraph.search import (
    find_nodes_by_name,
    find_paths,
    find_dependents,
    find_dependencies,
)


def parse_search_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="depgraph-search",
        description="Query the dependency graph of a Python project.",
    )
    parser.add_argument("path", help="Directory or file to analyse.")
    sub = parser.add_subparsers(dest="command", required=True)

    # find-node
    p_find = sub.add_parser("find-node", help="Find nodes whose name contains a pattern.")
    p_find.add_argument("pattern")
    p_find.add_argument("--case-sensitive", action="store_true")

    # paths
    p_paths = sub.add_parser("paths", help="List all simple paths between two nodes.")
    p_paths.add_argument("source")
    p_paths.add_argument("target")

    # dependents
    p_dep = sub.add_parser("dependents", help="List all nodes that depend on a given node.")
    p_dep.add_argument("node")

    # dependencies
    p_deps = sub.add_parser("dependencies", help="List all nodes a given node depends on.")
    p_deps.add_argument("node")

    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> None:  # pragma: no cover
    args = parse_search_args(argv)
    files = collect_python_files(args.path)
    graph = build_dependency_graph(files)

    if args.command == "find-node":
        matches = find_nodes_by_name(graph, args.pattern, args.case_sensitive)
        if not matches:
            print("No nodes found.", file=sys.stderr)
        else:
            for m in matches:
                print(m)

    elif args.command == "paths":
        paths = find_paths(graph, args.source, args.target)
        if not paths:
            print(f"No path from {args.source!r} to {args.target!r}.", file=sys.stderr)
        else:
            for p in paths:
                print(" -> ".join(p))

    elif args.command == "dependents":
        nodes = find_dependents(graph, args.node)
        if not nodes:
            print(f"No dependents for {args.node!r}.", file=sys.stderr)
        else:
            for n in nodes:
                print(n)

    elif args.command == "dependencies":
        nodes = find_dependencies(graph, args.node)
        if not nodes:
            print(f"{args.node!r} has no dependencies.", file=sys.stderr)
        else:
            for n in nodes:
                print(n)


if __name__ == "__main__":  # pragma: no cover
    main()
