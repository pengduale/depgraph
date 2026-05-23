"""CLI command: depgraph-annotate — print node annotations for a project."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from depgraph.cli import collect_python_files
from depgraph.parser import extract_imports, build_dependency_graph
from depgraph.annotator import annotate_nodes, filter_by_annotation


def parse_annotate_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="depgraph-annotate",
        description="Annotate dependency-graph nodes with structural labels.",
    )
    parser.add_argument(
        "path",
        help="Python file or directory to analyse.",
    )
    parser.add_argument(
        "--filter",
        metavar="LABEL",
        dest="label_filter",
        default=None,
        help="Only show nodes with this label (cycle, entry, leaf, isolated).",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:  # pragma: no cover
    args = parse_annotate_args(argv)

    files = collect_python_files(Path(args.path))
    imports_map = {f: extract_imports(f) for f in files}
    graph = build_dependency_graph(imports_map)

    annotations = annotate_nodes(graph)

    if args.label_filter:
        nodes = filter_by_annotation(annotations, args.label_filter)
        if args.format == "json":
            print(json.dumps(nodes, indent=2))
        else:
            if not nodes:
                print(f"No nodes with label '{args.label_filter}'.")
            else:
                for node in nodes:
                    print(node)
        return

    if args.format == "json":
        print(json.dumps(annotations, indent=2))
    else:
        for node, labels in sorted(annotations.items()):
            label_str = ", ".join(labels) if labels else "-"
            print(f"{node}: {label_str}")


if __name__ == "__main__":  # pragma: no cover
    main(sys.argv[1:])
