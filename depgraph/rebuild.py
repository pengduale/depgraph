"""Orchestrates a full dependency graph rebuild and optional SVG/export output."""

from pathlib import Path
from typing import Optional

from depgraph.cli import collect_python_files
from depgraph.parser import build_dependency_graph
from depgraph.renderer import render_svg
from depgraph.exporter import save_export


def rebuild(
    paths: list[str],
    output_svg: Optional[str] = None,
    export_format: Optional[str] = None,
    export_path: Optional[str] = None,
    verbose: bool = False,
) -> dict:
    """Collect files from *paths*, rebuild the dependency graph, and write outputs.

    Returns the dependency graph dict ``{module: [deps, ...]}``.  
    """
    files: list[str] = []
    for p in paths:
        files.extend(collect_python_files(p))

    if not files:
        if verbose:
            print("[rebuild] No Python files found.")
        return {}

    graph = build_dependency_graph(files)

    if verbose:
        print(f"[rebuild] {len(files)} files → {len(graph)} modules")

    if output_svg:
        svg = render_svg(graph)
        Path(output_svg).write_text(svg, encoding="utf-8")
        if verbose:
            print(f"[rebuild] SVG written to {output_svg}")

    if export_format and export_path:
        save_export(graph, export_path, fmt=export_format)
        if verbose:
            print(f"[rebuild] Export ({export_format}) written to {export_path}")

    return graph
