"""CLI entry-point for the node scorer."""

from __future__ import annotations

import argparse
import json
import sys

from depgraph.cli import collect_python_files
from depgraph.parser import build_dependency_graph, extract_imports
from depgraph.scorer import format_scores, rank_nodes, score_nodes


def parse_scorer_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="depgraph-score",
        description="Score and rank nodes in a Python dependency graph.",
    )
    parser.add_argument(
        "path",
        help="Python file or directory to analyse.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=None,
        metavar="N",
        help="Show only the top N nodes.",
    )
    parser.add_argument(
        "--in-weight",
        type=float,
        default=0.6,
        dest="in_weight",
        metavar="W",
        help="Weight for in-degree contribution (default: 0.6).",
    )
    parser.add_argument(
        "--out-weight",
        type=float,
        default=0.4,
        dest="out_weight",
        metavar="W",
        help="Weight for out-degree contribution (default: 0.4).",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:  # pragma: no cover
    args = parse_scorer_args(argv)

    files = collect_python_files(args.path)
    if not files:
        print("No Python files found.", file=sys.stderr)
        sys.exit(1)

    graph: dict[str, list[str]] = {}
    for f in files:
        imports = extract_imports(f)
        graph = build_dependency_graph(graph, f, imports)

    scores = score_nodes(graph, in_weight=args.in_weight, out_weight=args.out_weight)
    ranked = rank_nodes(scores, top=args.top)

    if args.format == "json":
        print(json.dumps({node: score for node, score in ranked}, indent=2))
    else:
        print(format_scores(ranked))
