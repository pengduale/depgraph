"""CLI entry-point for the dependency-graph linter."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from depgraph.cli import collect_python_files
from depgraph.parser import build_dependency_graph, extract_imports
from depgraph.linter import LintIssue, format_issues, run_linter


def parse_linter_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="depgraph-lint",
        description="Lint a Python project's dependency graph for structural issues.",
    )
    parser.add_argument(
        "path",
        help="File or directory to analyse.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with code 1 when issues are found.",
    )
    parser.add_argument(
        "--only",
        metavar="CODE",
        nargs="+",
        help="Only report issues with these codes (e.g. E001 W001).",
    )
    return parser.parse_args(argv)


def _issues_to_dict(issues: List[LintIssue]) -> list:
    return [
        {"code": i.code, "message": i.message, "nodes": i.nodes}
        for i in issues
    ]


def main(argv: List[str] | None = None) -> None:
    args = parse_linter_args(argv)

    files = collect_python_files(args.path)
    graph: dict = {}
    for f in files:
        imports = extract_imports(f)
        graph = build_dependency_graph(graph, f, imports)

    issues = run_linter(graph)

    if args.only:
        codes = set(args.only)
        issues = [i for i in issues if i.code in codes]

    if args.format == "json":
        print(json.dumps(_issues_to_dict(issues), indent=2))
    else:
        print(format_issues(issues))

    if args.exit_code and issues:
        sys.exit(1)


if __name__ == "__main__":
    main()
