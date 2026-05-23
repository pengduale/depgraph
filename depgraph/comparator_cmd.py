"""CLI entry-point for comparing two graph snapshots."""

from __future__ import annotations

import argparse
import json
import sys

from depgraph.snapshot import load_snapshot
from depgraph.comparator import compare_graphs, format_comparison, is_identical


def parse_compare_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="depgraph-compare",
        description="Compare two dependency-graph snapshots.",
    )
    parser.add_argument("old", help="Path to the older snapshot JSON file.")
    parser.add_argument("new", help="Path to the newer snapshot JSON file.")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with code 1 when graphs differ.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_compare_args(argv)

    old_graph = load_snapshot(args.old)
    new_graph = load_snapshot(args.new)

    comparison = compare_graphs(old_graph, new_graph)
    identical = is_identical(old_graph, new_graph)

    if args.format == "json":
        # Convert tuple edges to lists for JSON serialisation
        serialisable = {
            k: [list(e) if isinstance(e, tuple) else e for e in v]
            for k, v in comparison.items()
        }
        print(json.dumps(serialisable, indent=2))
    else:
        if identical:
            print("Graphs are identical.")
        else:
            print(format_comparison(comparison))

    if args.exit_code and not identical:
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
