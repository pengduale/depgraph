"""Save and load graph snapshots for diff comparisons."""

import json
import os
from typing import Dict, Set

Graph = Dict[str, Set[str]]

_DEFAULT_PATH = ".depgraph_snapshot.json"


def save_snapshot(graph: Graph, path: str = _DEFAULT_PATH) -> None:
    """Persist *graph* to *path* as JSON.

    Sets are serialised as sorted lists so the file is stable for VCS.
    """
    serialisable = {node: sorted(deps) for node, deps in graph.items()}
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(serialisable, fh, indent=2, sort_keys=True)
        fh.write("\n")


def load_snapshot(path: str = _DEFAULT_PATH) -> Graph:
    """Load a previously saved snapshot from *path*.

    Returns an empty graph if the file does not exist.
    """
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        raw = json.load(fh)
    return {node: set(deps) for node, deps in raw.items()}


def snapshot_exists(path: str = _DEFAULT_PATH) -> bool:
    """Return True when a snapshot file is present at *path*."""
    return os.path.isfile(path)
