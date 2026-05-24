"""CLI command for tracing dependency chains between two nodes."""

import argparse
import json
import sys

from depgraph.cli import collect_python_files
from depgraph.parser import build_dependency_graph
from depgraph.tracer import chain_summary, format_chain


def parse_tracer_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Trace dependency chains between two modules."
    )
    parser.add_argument("path", help="File or directory to analyse")
    parser.add_argument("source", help="Source module name")
    parser.add_argument("target", help="Target module name")
    parser.add_argument(
        "--all",
        dest="all_chains",
        action="store_true",
        help="Show all chains, not just the shortest",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_tracer_args(argv)
    files = collect_python_files(args.path)
    graph = build_dependency_graph(files)

    summary = chain_summary(graph, args.source, args.target)

    if args.format == "json":
        print(json.dumps(summary, indent=2))
        sys.exit(0 if summary["reachable"] else 1)

    # text output
    if not summary["reachable"]:
        print(f"No path from '{args.source}' to '{args.target}'.")
        sys.exit(1)

    if args.all_chains:
        print(
            f"{summary['chain_count']} chain(s) from '{args.source}' to '{args.target}':"
        )
        for chain in summary["all_chains"]:
            print(" ", format_chain(chain))
    else:
        print(
            f"Shortest chain ({summary['shortest_length']} hop(s)): "
            f"{format_chain(summary['shortest'])}"
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
