"""CLI entry-point for the heatmap command."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from depgraph.cli import collect_python_files
from depgraph.parser import build_dependency_graph, extract_imports
from depgraph.heatmap import build_heatmap, compute_heat, format_heatmap


def parse_heatmap_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="depgraph-heatmap",
        description="Show node heat based on graph metrics.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Python file or directory to analyse (default: current directory).",
    )
    parser.add_argument(
        "--metric",
        choices=["in_degree", "out_degree", "total_degree"],
        default="in_degree",
        help="Metric used to compute heat (default: in_degree).",
    )
    parser.add_argument(
        "--palette",
        choices=["red", "blue", "green"],
        default="red",
        help="Colour palette for the heatmap (default: red).",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
        help="Output format (default: text).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_heatmap_args(argv)

    files = collect_python_files(args.path)
    if not files:
        print("No Python files found.", file=sys.stderr)
        sys.exit(1)

    graph: dict = {}
    for f in files:
        source = Path(f).read_text(encoding="utf-8", errors="ignore")
        imports = extract_imports(source)
        graph = build_dependency_graph(graph, f, imports)

    heat = compute_heat(graph, metric=args.metric)
    colors = build_heatmap(graph, metric=args.metric, palette=args.palette)

    if args.fmt == "json":
        output = {
            node: {"heat": round(heat[node], 4), "color": colors[node]}
            for node in sorted(heat)
        }
        print(json.dumps(output, indent=2))
    else:
        print(f"Metric : {args.metric}")
        print(f"Palette: {args.palette}")
        print()
        print(format_heatmap(heat))


if __name__ == "__main__":  # pragma: no cover
    main()
