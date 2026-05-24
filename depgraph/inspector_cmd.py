"""CLI entry point for the node/edge inspector."""
from __future__ import annotations

import argparse
import json
import sys

from depgraph.cli import collect_python_files
from depgraph.parser import build_dependency_graph, extract_imports
from depgraph.inspector import (
    find_bottlenecks,
    format_node_report,
    inspect_edge,
    inspect_node,
)


def parse_inspector_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="depgraph-inspect",
        description="Inspect nodes and edges in a dependency graph.",
    )
    p.add_argument("path", help="Python file or directory to analyse")
    p.add_argument("--node", metavar="NAME", help="Inspect a specific node")
    p.add_argument(
        "--edge",
        metavar="SRC:DST",
        help="Inspect a specific edge (e.g. pkg.a:pkg.b)",
    )
    p.add_argument(
        "--bottlenecks",
        metavar="N",
        type=int,
        default=None,
        help="List nodes with in-degree >= N",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
        help="Output format (default: text)",
    )
    return p.parse_args(argv)


def main(argv=None) -> None:
    args = parse_inspector_args(argv)

    files = collect_python_files(args.path)
    imports = {f: extract_imports(f) for f in files}
    graph = build_dependency_graph(imports)

    if args.node:
        info = inspect_node(graph, args.node)
        if args.fmt == "json":
            print(json.dumps(info, indent=2))
        else:
            print(format_node_report(info))
        return

    if args.edge:
        if ":" not in args.edge:
            print("--edge must be in SRC:DST format", file=sys.stderr)
            sys.exit(1)
        src, dst = args.edge.split(":", 1)
        info = inspect_edge(graph, src, dst)
        if args.fmt == "json":
            print(json.dumps(info, indent=2))
        else:
            for k, v in info.items():
                print(f"{k}: {v}")
        return

    if args.bottlenecks is not None:
        nodes = find_bottlenecks(graph, args.bottlenecks)
        if args.fmt == "json":
            print(json.dumps(nodes, indent=2))
        else:
            if nodes:
                print("\n".join(nodes))
            else:
                print("No bottleneck nodes found.")
        return

    print("Specify --node, --edge, or --bottlenecks.", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
