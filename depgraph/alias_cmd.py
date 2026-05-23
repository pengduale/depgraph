"""CLI sub-command: manage and apply module aliases."""

from __future__ import annotations

import argparse
import json
import sys

from depgraph.alias import build_alias_map, apply_aliases
from depgraph.parser import build_dependency_graph
from depgraph.cli import collect_python_files
from depgraph.exporter import export_json


def parse_alias_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="depgraph-alias",
        description="Apply module aliases to a dependency graph.",
    )
    parser.add_argument(
        "path",
        help="Python file or directory to analyse.",
    )
    parser.add_argument(
        "--alias",
        metavar="ALIAS=FULL",
        action="append",
        default=[],
        dest="aliases",
        help="Alias definition, e.g. 'core=myproject.core'. Repeatable.",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text).",
    )
    return parser.parse_args(argv)


def _parse_alias_pair(raw: str) -> tuple[str, str]:
    if "=" not in raw:
        raise argparse.ArgumentTypeError(
            f"Alias must be in ALIAS=FULL format, got: {raw!r}"
        )
    alias, _, full_path = raw.partition("=")
    return alias.strip(), full_path.strip()


def main(argv: list[str] | None = None) -> None:
    args = parse_alias_args(argv)

    try:
        pairs = [_parse_alias_pair(a) for a in args.aliases]
    except argparse.ArgumentTypeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        alias_map = build_alias_map(pairs)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)

    files = collect_python_files(args.path)
    graph = build_dependency_graph(files)

    resolved = apply_aliases(graph, alias_map)

    if args.format == "json":
        print(export_json(resolved))
    else:
        if not resolved:
            print("(empty graph)")
            return
        for node in sorted(resolved):
            deps = resolved[node]
            dep_str = ", ".join(sorted(deps)) if deps else "(none)"
            print(f"{node} -> {dep_str}")


if __name__ == "__main__":
    main()
