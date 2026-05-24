"""CLI command: split a dependency graph into connected components."""

from __future__ import annotations

import argparse
import json
import sys

from depgraph.cli import collect_python_files
from depgraph.parser import build_dependency_graph
from depgraph.splitter import split_components, component_count


def parse_splitter_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="depgraph-split",
        description="Split dependency graph into weakly connected components.",
    )
    parser.add_argument(
        "path",
        help="Python file or directory to analyse.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--min-size",
        type=int,
        default=1,
        metavar="N",
        help="Only show components with at least N nodes (default: 1).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_splitter_args(argv)
    files = collect_python_files(args.path)
    graph = build_dependency_graph(files)
    components = [
        c for c in split_components(graph) if len(c) >= args.min_size
    ]

    if args.format == "json":
        output = [
            {"component": i + 1, "nodes": sorted(c.keys()), "graph": c}
            for i, c in enumerate(components)
        ]
        print(json.dumps(output, indent=2))
    else:
        total = component_count(graph)
        print(f"Total components: {total}  (showing {len(components)} with min-size={args.min_size})")
        for i, comp in enumerate(components, 1):
            nodes = sorted(comp.keys())
            print(f"\nComponent {i} ({len(nodes)} node{'s' if len(nodes) != 1 else ''}):")
            for node in nodes:
                deps = comp[node]
                if deps:
                    print(f"  {node} -> {', '.join(sorted(deps))}")
                else:
                    print(f"  {node}")


if __name__ == "__main__":  # pragma: no cover
    main(sys.argv[1:])
