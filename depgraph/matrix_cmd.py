"""CLI command: depgraph-matrix — print adjacency matrix for a project."""

from __future__ import annotations
import argparse
import sys

from depgraph.parser import extract_imports, build_dependency_graph
from depgraph.cli import collect_python_files
from depgraph.matrix import build_matrix, format_matrix, density


def parse_matrix_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="depgraph-matrix",
        description="Print the adjacency matrix of a Python project's import graph.",
    )
    p.add_argument("path", help="File or directory to analyse")
    p.add_argument(
        "--density",
        action="store_true",
        help="Print edge density instead of the full matrix",
    )
    p.add_argument(
        "--no-header",
        dest="no_header",
        action="store_true",
        help="Suppress the column-header row",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_matrix_args(argv)

    files = collect_python_files(args.path)
    if not files:
        print("No Python files found.", file=sys.stderr)
        sys.exit(1)

    imports_map = {f: extract_imports(f) for f in files}
    graph = build_dependency_graph(imports_map)

    nodes, matrix = build_matrix(graph)

    if args.density:
        print(f"{density(matrix):.4f}")
        return

    output = format_matrix(nodes, matrix)
    if args.no_header:
        lines = output.splitlines()
        output = "\n".join(lines[1:]) if len(lines) > 1 else ""

    print(output)


if __name__ == "__main__":
    main()
