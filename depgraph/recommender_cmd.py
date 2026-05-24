"""CLI entry-point for the recommender module."""

from __future__ import annotations

import argparse
import json
import sys
from typing import List

from depgraph.cli import collect_python_files
from depgraph.parser import build_dependency_graph, extract_imports
from depgraph.recommender import (
    Recommendation,
    format_recommendations,
    get_recommendations,
)


def parse_recommender_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="depgraph-recommend",
        description="Suggest refactoring actions for a Python project.",
    )
    parser.add_argument(
        "path",
        help="File or directory to analyse.",
    )
    parser.add_argument(
        "--coupling-threshold",
        type=int,
        default=5,
        metavar="N",
        help="Max allowed out-degree before flagging high coupling (default: 5).",
    )
    parser.add_argument(
        "--god-threshold",
        type=int,
        default=5,
        metavar="N",
        help="Max allowed in-degree before flagging a god module (default: 5).",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--severity",
        choices=["error", "warning", "info"],
        default=None,
        help="Filter output to a specific severity level.",
    )
    return parser.parse_args(argv)


def _recs_to_dicts(recs: List[Recommendation]) -> List[dict]:
    return [
        {
            "node": r.node,
            "category": r.category,
            "severity": r.severity,
            "message": r.message,
        }
        for r in recs
    ]


def main(argv: List[str] | None = None) -> None:
    args = parse_recommender_args(argv)

    files = collect_python_files(args.path)
    graph: dict = {}
    for f in files:
        imports = extract_imports(f)
        graph = build_dependency_graph(graph, f, imports)

    recs = get_recommendations(
        graph,
        coupling_threshold=args.coupling_threshold,
        god_threshold=args.god_threshold,
    )

    if args.severity:
        recs = [r for r in recs if r.severity == args.severity]

    if args.format == "json":
        print(json.dumps(_recs_to_dicts(recs), indent=2))
    else:
        print(format_recommendations(recs))

    has_errors = any(r.severity == "error" for r in recs)
    sys.exit(1 if has_errors else 0)


if __name__ == "__main__":  # pragma: no cover
    main()
