"""CLI entry-point for the cluster sub-command."""

from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from depgraph.cli import collect_python_files
from depgraph.parser import build_dependency_graph
from depgraph.cluster import cluster_by_prefix, merge_small_clusters, cluster_summary


def parse_cluster_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="depgraph-cluster",
        description="Cluster project modules by dotted-prefix.",
    )
    parser.add_argument(
        "path",
        help="Path to a Python file or directory to analyse.",
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=1,
        help="Prefix depth used to form cluster keys (default: 1).",
    )
    parser.add_argument(
        "--min-size",
        type=int,
        default=1,
        dest="min_size",
        help="Merge clusters smaller than this into 'other' (default: 1).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Output result as JSON.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> None:  # pragma: no cover
    args = parse_cluster_args(argv)

    files = collect_python_files(args.path)
    if not files:
        print("No Python files found.", file=sys.stderr)
        sys.exit(1)

    graph = build_dependency_graph(files)
    nodes = list(graph.keys())

    clusters = cluster_by_prefix(nodes, depth=args.depth)
    if args.min_size > 1:
        clusters = merge_small_clusters(clusters, min_size=args.min_size)

    summary = cluster_summary(clusters)

    if args.as_json:
        print(json.dumps(summary, indent=2))
    else:
        for entry in summary:
            print(f"[{entry['cluster']}] ({entry['size']} nodes)")
            for member in entry["members"]:
                print(f"  - {member}")


if __name__ == "__main__":  # pragma: no cover
    main()
