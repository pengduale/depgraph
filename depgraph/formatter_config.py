"""Default configuration and style registry for the formatter module."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class FormatterConfig:
    """Holds user-configurable options for graph formatting."""

    style: str = "adjacency"
    """One of ``adjacency``, ``edges``, ``table``."""

    prefix_filter: str | None = None
    """If set, only nodes whose name starts with this string are shown."""

    max_nodes: int | None = None
    """Truncate output after this many nodes (``None`` = unlimited)."""

    sort_output: bool = True
    """Whether to sort nodes/edges alphabetically."""


AVAILABLE_STYLES: List[str] = ["adjacency", "edges", "table"]

STYLE_DESCRIPTIONS: Dict[str, str] = {
    "adjacency": "Each node followed by its comma-separated dependencies.",
    "edges": "One directed edge per line in 'source -> target' notation.",
    "table": "Two-column padded table with Source and Target headers.",
}


def default_config() -> FormatterConfig:
    """Return a ``FormatterConfig`` with all defaults."""
    return FormatterConfig()


def config_from_dict(data: dict) -> FormatterConfig:
    """Build a ``FormatterConfig`` from a plain dictionary (e.g. parsed JSON)."""
    cfg = FormatterConfig()
    if "style" in data:
        if data["style"] not in AVAILABLE_STYLES:
            raise ValueError(
                f"Invalid style {data['style']!r}. Choose from {AVAILABLE_STYLES}."
            )
        cfg.style = data["style"]
    if "prefix_filter" in data:
        cfg.prefix_filter = data["prefix_filter"]
    if "max_nodes" in data:
        cfg.max_nodes = int(data["max_nodes"])
    if "sort_output" in data:
        cfg.sort_output = bool(data["sort_output"])
    return cfg
