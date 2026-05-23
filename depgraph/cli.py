"""Command-line interface for depgraph."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

from depgraph.parser import extract_imports, build_dependency_graph
from depgraph.renderer import render_svg
from depgraph.exporter import save_export
from depgraph.filter import (
    filter_by_prefix,
    filter_by_depth,
    exclude_nodes,
    remove_isolated_nodes,
)


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="depgraph",
        description="Visualize Python project dependency graphs.",
    )
    parser.add_argument("path", help="File or directory to analyse")
    parser.add_argument("-o", "--output", default="depgraph.svg", help="Output file path")
    parser.add_argument("--format", choices=["svg", "json", "dot"], default="svg")
    parser.add_argument("--prefix", default=None, help="Filter nodes by module prefix")
    parser.add_argument("--exclude", nargs="*", default=[], metavar="MODULE",
                        help="Modules to exclude from the graph")
    parser.add_argument("--depth", type=int, default=None, metavar="N",
                        help="Limit graph depth from a root node (requires --root)")
    parser.add_argument("--root", default=None,
                        help="Root module for depth-limited traversal")
    parser.add_argument("--no-isolated", action="store_true",
                        help="Remove isolated (unconnected) nodes")
    return parser.parse_args(argv)


def collect_python_files(path: str) -> List[Path]:
    p = Path(path)
    if p.is_file() and p.suffix == ".py":
        return [p]
    if p.is_dir():
        return sorted(p.rglob("*.py"))
    return []


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv)
    files = collect_python_files(args.path)

    if not files:
        print(f"No Python files found at: {args.path}", file=sys.stderr)
        return 1

    imports_map = {str(f): extract_imports(f.read_text()) for f in files}
    graph = build_dependency_graph(imports_map)

    if args.prefix:
        graph = filter_by_prefix(graph, args.prefix)

    if args.exclude:
        graph = exclude_nodes(graph, args.exclude)

    if args.depth is not None:
        if not args.root:
            print("--depth requires --root to be specified.", file=sys.stderr)
            return 1
        graph = filter_by_depth(graph, args.root, args.depth)

    if args.no_isolated:
        graph = remove_isolated_nodes(graph)

    if args.format == "svg":
        svg = render_svg(graph)
        Path(args.output).write_text(svg)
    else:
        save_export(graph, args.output, fmt=args.format)

    print(f"Output written to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
