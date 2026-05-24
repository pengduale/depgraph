"""Configuration dataclass for the inspector module."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class InspectorConfig:
    """Settings that control inspector behaviour."""

    # Minimum in-degree to classify a node as a bottleneck
    bottleneck_threshold: int = 2

    # Fields to include in text reports
    report_fields: List[str] = field(
        default_factory=lambda: [
            "node",
            "in_degree",
            "out_degree",
            "dependencies",
            "dependents",
            "is_root",
            "is_leaf",
            "is_isolated",
        ]
    )

    # Whether to sort output lists alphabetically
    sort_output: bool = True


def default_inspector_config() -> InspectorConfig:
    """Return a config with all defaults applied."""
    return InspectorConfig()


def inspector_config_from_dict(data: dict) -> InspectorConfig:
    """Build an InspectorConfig from a plain dictionary (e.g. loaded from JSON)."""
    cfg = InspectorConfig()
    if "bottleneck_threshold" in data:
        cfg.bottleneck_threshold = int(data["bottleneck_threshold"])
    if "report_fields" in data:
        cfg.report_fields = list(data["report_fields"])
    if "sort_output" in data:
        cfg.sort_output = bool(data["sort_output"])
    return cfg
