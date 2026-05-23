"""Tests for depgraph.snapshot."""

import json
import os
import pytest

from depgraph.snapshot import save_snapshot, load_snapshot, snapshot_exists


@pytest.fixture
def tmp_path_snap(tmp_path):
    return str(tmp_path / "snap.json")


def test_save_creates_file(tmp_path_snap):
    save_snapshot({"a": {"b"}, "b": set()}, tmp_path_snap)
    assert os.path.isfile(tmp_path_snap)


def test_save_and_load_roundtrip(tmp_path_snap):
    graph = {"a": {"b", "c"}, "b": {"c"}, "c": set()}
    save_snapshot(graph, tmp_path_snap)
    loaded = load_snapshot(tmp_path_snap)
    assert loaded == graph


def test_save_uses_sorted_lists(tmp_path_snap):
    save_snapshot({"x": {"z", "a", "m"}}, tmp_path_snap)
    with open(tmp_path_snap) as fh:
        raw = json.load(fh)
    assert raw["x"] == sorted(raw["x"])


def test_load_missing_file_returns_empty(tmp_path):
    result = load_snapshot(str(tmp_path / "nonexistent.json"))
    assert result == {}


def test_load_returns_sets(tmp_path_snap):
    save_snapshot({"a": {"b"}}, tmp_path_snap)
    loaded = load_snapshot(tmp_path_snap)
    assert isinstance(loaded["a"], set)


def test_snapshot_exists_true(tmp_path_snap):
    save_snapshot({}, tmp_path_snap)
    assert snapshot_exists(tmp_path_snap) is True


def test_snapshot_exists_false(tmp_path):
    assert snapshot_exists(str(tmp_path / "nope.json")) is False


def test_save_empty_graph(tmp_path_snap):
    save_snapshot({}, tmp_path_snap)
    loaded = load_snapshot(tmp_path_snap)
    assert loaded == {}


def test_file_ends_with_newline(tmp_path_snap):
    save_snapshot({"a": set()}, tmp_path_snap)
    with open(tmp_path_snap, "rb") as fh:
        content = fh.read()
    assert content.endswith(b"\n")
