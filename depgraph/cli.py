"""Command-line interface for depgraph."""

import argparse
import os
import sys
from pathlib import Path

from depgraph.parser import build_dependency_graph
from depgraph.renderer import render_svg


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="depgraph",
        description="Visualize dependency graphs for Python projects as interactive SVG diagrams.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to the Python project or file (default: current directory)",
    )
    parser.add_argument(
        "-o", "--output",
        default="depgraph.svg",
        help="Output SVG file path (default: depgraph.svg)",
    )
    parser.add_argument(
        "--exclude",
        nargs="*",
        default=[],
        metavar="MODULE",
        help="Module names to exclude from the graph",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Do not open the SVG file after generation",
    )
    return parser.parse_args(argv)


def collect_python_files(root):
    """Recursively collect all .py files under root."""
    root = Path(root)
    if root.is_file() and root.suffix == ".py":
        return [root]
    return sorted(root.rglob("*.py"))


def main(argv=None):
    args = parse_args(argv)
    target = Path(args.path)

    if not target.exists():
        print(f"error: path '{target}' does not exist.", file=sys.stderr)
        return 1

    py_files = collect_python_files(target)
    if not py_files:
        print(f"No Python files found in '{target}'.", file=sys.stderr)
        return 1

    print(f"Found {len(py_files)} Python file(s). Building dependency graph...")

    graph = build_dependency_graph(py_files, exclude=set(args.exclude))

    if not graph:
        print("No dependencies found.")
        return 0

    svg_content = render_svg(graph)
    output_path = Path(args.output)
    output_path.write_text(svg_content, encoding="utf-8")
    print(f"SVG written to '{output_path}'.")

    if not args.no_open:
        import webbrowser
        webbrowser.open(output_path.resolve().as_uri())

    return 0


if __name__ == "__main__":
    sys.exit(main())
