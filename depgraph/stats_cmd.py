"""CLI entry-point for the 'depgraph stats' sub-command."""

from __future__ import annotations

import argparse
import json
import sys

from depgraph.cli import collect_python_files
from depgraph.parser import extract_imports, build_dependency_graph
from depgraph.stats import compute_stats, format_stats


def parse_stats_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="depgraph-stats",
        description="Print summary statistics for a Python project's dependency graph.",
    )
    parser.add_argument(
        "path",
        help="File or directory to analyse.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Output statistics as JSON instead of plain text.",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        help="JSON indentation level (default: 2).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:  # pragma: no cover
    args = parse_stats_args(argv)

    files = collect_python_files(args.path)
    if not files:
        print(f"No Python files found at: {args.path}", file=sys.stderr)
        sys.exit(1)

    imports_map = {f: extract_imports(f) for f in files}
    graph = build_dependency_graph(imports_map)
    stats = compute_stats(graph)

    if args.as_json:
        print(json.dumps(stats, indent=args.indent))
    else:
        print(format_stats(stats))


if __name__ == "__main__":  # pragma: no cover
    main()
