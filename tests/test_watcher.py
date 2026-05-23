"""Tests for depgraph.watcher and depgraph.rebuild."""

import time
from pathlib import Path

import pytest

from depgraph.watcher import _collect_mtimes, _detect_changes, watch
from depgraph.rebuild import rebuild


# ---------------------------------------------------------------------------
# _collect_mtimes
# ---------------------------------------------------------------------------

def test_collect_mtimes_single_file(tmp_path):
    f = tmp_path / "a.py"
    f.write_text("x = 1")
    mtimes = _collect_mtimes([str(f)])
    assert str(f) in mtimes
    assert isinstance(mtimes[str(f)], float)


def test_collect_mtimes_directory(tmp_path):
    (tmp_path / "mod.py").write_text("")
    (tmp_path / "other.txt").write_text("")
    mtimes = _collect_mtimes([str(tmp_path)])
    keys = list(mtimes.keys())
    assert all(k.endswith(".py") for k in keys)
    assert len(keys) == 1


def test_collect_mtimes_missing_path():
    # Non-existent paths should not raise; they simply produce no entries
    mtimes = _collect_mtimes(["/nonexistent/path"])
    assert mtimes == {}


# ---------------------------------------------------------------------------
# _detect_changes
# ---------------------------------------------------------------------------

def test_detect_changes_added():
    old = {"a.py": 1.0}
    new = {"a.py": 1.0, "b.py": 2.0}
    added, modified, removed = _detect_changes(old, new)
    assert added == ["b.py"]
    assert modified == []
    assert removed == []


def test_detect_changes_removed():
    old = {"a.py": 1.0, "b.py": 2.0}
    new = {"a.py": 1.0}
    added, modified, removed = _detect_changes(old, new)
    assert removed == ["b.py"]
    assert added == []
    assert modified == []


def test_detect_changes_modified():
    old = {"a.py": 1.0}
    new = {"a.py": 9.0}
    added, modified, removed = _detect_changes(old, new)
    assert modified == ["a.py"]
    assert added == []
    assert removed == []


def test_detect_changes_no_changes():
    snap = {"a.py": 1.0, "b.py": 2.0}
    added, modified, removed = _detect_changes(snap, snap.copy())
    assert added == modified == removed == []


# ---------------------------------------------------------------------------
# watch (limited iterations)
# ---------------------------------------------------------------------------

def test_watch_callback_triggered_on_modification(tmp_path):
    f = tmp_path / "mod.py"
    f.write_text("x = 1")

    events = []

    def cb(added, modified, removed):
        events.append((added, modified, removed))

    # Modify the file after a tiny delay so mtime changes
    original = f.stat().st_mtime
    f.write_text("x = 2")
    import os; os.utime(str(f), (original + 5, original + 5))

    watch([str(tmp_path)], cb, interval=0.05, max_iterations=2)
    assert len(events) >= 1


# ---------------------------------------------------------------------------
# rebuild
# ---------------------------------------------------------------------------

def test_rebuild_returns_graph(tmp_path):
    (tmp_path / "alpha.py").write_text("import beta")
    (tmp_path / "beta.py").write_text("")
    graph = rebuild([str(tmp_path)])
    assert isinstance(graph, dict)


def test_rebuild_writes_svg(tmp_path):
    (tmp_path / "a.py").write_text("")
    svg_out = tmp_path / "out.svg"
    rebuild([str(tmp_path)], output_svg=str(svg_out))
    assert svg_out.exists()
    assert "<svg" in svg_out.read_text()


def test_rebuild_empty_paths_returns_empty(tmp_path):
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    graph = rebuild([str(empty_dir)])
    assert graph == {}
