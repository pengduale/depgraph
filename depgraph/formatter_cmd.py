"""CLI entry point for the formatter module."""

from __future__ import annotations

import argparse
import sys

from depgraph.cli import collect_python_files
from depgraph.parser import build_dependency_graph, extract_imports
from depgraph.formatter import format_graph


def parse_formatter_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="depgraph-format",
        description="Print a dependency graph in a chosen text format.",
    )
    parser.add_argument(
        "path",
        help="Python file or directory to analyse.",
    )
    parser.add_argument(
        "--style",
        choices=["adjacency", "edges", "table"],
        default="adjacency",
        help="Output style (default: adjacency).",
    )
    parser.add_argument(
        "--prefix",
        default=None,
        help="Only include nodes whose names start with this prefix.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_formatter_args(argv)
    files = collect_python_files(args.path)
    imports = {}
    for f in files:
        imports.update(extract_imports(f))
    graph = build_dependency_graph(imports)
    if args.prefix:
        graph = {k: [d for d in v if d.startswith(args.prefix)]
                 for k, v in graph.items() if k.startswith(args.prefix)}
    print(format_graph(graph, style=args.style))


if __name__ == "__main__":  # pragma: no cover
    main()
