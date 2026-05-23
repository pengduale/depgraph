"""File system watcher that triggers dependency graph rebuilds on source changes."""

import time
import os
from pathlib import Path
from typing import Callable, Dict, Optional


def _collect_mtimes(paths: list[str]) -> Dict[str, float]:
    """Return a mapping of file path -> last modified time."""
    mtimes: Dict[str, float] = {}
    for p in paths:
        path = Path(p)
        if path.is_dir():
            for f in path.rglob("*.py"):
                mtimes[str(f)] = f.stat().st_mtime
        elif path.is_file() and path.suffix == ".py":
            mtimes[str(path)] = path.stat().st_mtime
    return mtimes


def _detect_changes(
    old: Dict[str, float], new: Dict[str, float]
) -> tuple[list[str], list[str], list[str]]:
    """Return (added, modified, removed) file lists."""
    added = [f for f in new if f not in old]
    removed = [f for f in old if f not in new]
    modified = [
        f for f in new if f in old and new[f] != old[f]
    ]
    return added, modified, removed


def watch(
    paths: list[str],
    callback: Callable[[list[str], list[str], list[str]], None],
    interval: float = 1.0,
    max_iterations: Optional[int] = None,
) -> None:
    """Poll *paths* every *interval* seconds and invoke *callback* on changes.

    Args:
        paths: Directories or files to watch.
        callback: Called with (added, modified, removed) when changes detected.
        interval: Polling interval in seconds.
        max_iterations: Stop after this many iterations (useful for testing).
    """
    current_mtimes = _collect_mtimes(paths)
    iterations = 0

    while True:
        time.sleep(interval)
        new_mtimes = _collect_mtimes(paths)
        added, modified, removed = _detect_changes(current_mtimes, new_mtimes)

        if added or modified or removed:
            callback(added, modified, removed)
            current_mtimes = new_mtimes

        iterations += 1
        if max_iterations is not None and iterations >= max_iterations:
            break
