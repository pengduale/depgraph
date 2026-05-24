"""CLI entry-point for the renamer feature."""

from __future__ import annotations

import argparse
import json
import sys

from depgraph.parser import build_dependency_graph
from depgraph.cli import collect_python_files
from depgraph.renamer import rename_nodes, normalize_names, format_rename_diff


def parse_renamer_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="depgraph-rename",
        description="Rename nodes in a dependency graph.",
    )
    parser.add_argument(
        "path",
        help="Python file or directory to analyse.",
    )
    parser.add_argument(
        "--rename",
        metavar="OLD=NEW",
        action="append",
        default=[],
        help="Rename a node: --rename old.module=new.module (repeatable).",
    )
    parser.add_argument(
        "--normalize",
        action="store_true",
        help="Lowercase all node names.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
        help="Output format (default: text).",
    )
    return parser.parse_args(argv)


def _parse_pair(pair: str) -> tuple[str, str]:
    if "=" not in pair:
        raise argparse.ArgumentTypeError(
            f"Invalid rename spec '{pair}': expected OLD=NEW."
        )
    old, new = pair.split("=", 1)
    return old.strip(), new.strip()


def main(argv: list[str] | None = None) -> None:  # pragma: no cover
    args = parse_renamer_args(argv)
    files = collect_python_files(args.path)
    graph = build_dependency_graph(files)

    mapping = {}
    for spec in args.rename:
        old, new = _parse_pair(spec)
        mapping[old] = new

    original = {k: list(v) for k, v in graph.items()}

    if mapping:
        graph = rename_nodes(graph, mapping)
    if args.normalize:
        graph = normalize_names(graph)

    if args.fmt == "json":
        out = {node: sorted(deps) for node, deps in sorted(graph.items())}
        print(json.dumps(out, indent=2))
    else:
        print(format_rename_diff(original, graph))
        for node, deps in sorted(graph.items()):
            dep_str = ", ".join(sorted(deps)) if deps else "(none)"
            print(f"  {node}: {dep_str}")


if __name__ == "__main__":
    main(sys.argv[1:])
