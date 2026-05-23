"""Tests for depgraph.cluster_cmd."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from depgraph.cluster_cmd import parse_cluster_args, main


@pytest.fixture()
def tmp_project(tmp_path: Path) -> Path:
    pkg = tmp_path / "mypkg"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("")
    (pkg / "models.py").write_text("from mypkg import utils\n")
    (pkg / "views.py").write_text("from mypkg import models\n")
    (pkg / "utils.py").write_text("")
    return tmp_path


def test_parse_cluster_args_defaults():
    args = parse_cluster_args(["mydir"])
    assert args.path == "mydir"
    assert args.depth == 1
    assert args.min_size == 1
    assert args.as_json is False


def test_parse_cluster_args_custom():
    args = parse_cluster_args(["mydir", "--depth", "2", "--min-size", "3", "--json"])
    assert args.depth == 2
    assert args.min_size == 3
    assert args.as_json is True


def test_main_text_output(tmp_project: Path, capsys):
    main([str(tmp_project), "--depth", "1"])
    captured = capsys.readouterr()
    assert "mypkg" in captured.out


def test_main_json_output(tmp_project: Path, capsys):
    main([str(tmp_project), "--depth", "1", "--json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert isinstance(data, list)
    assert all("cluster" in entry for entry in data)
    assert all("size" in entry for entry in data)
    assert all("members" in entry for entry in data)


def test_main_json_size_matches_members(tmp_project: Path, capsys):
    """Verify that the reported size equals the actual number of members."""
    main([str(tmp_project), "--depth", "1", "--json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    for entry in data:
        assert entry["size"] == len(entry["members"]), (
            f"Cluster '{entry['cluster']}' reports size {entry['size']} "
            f"but has {len(entry['members'])} members"
        )


def test_main_min_size_filters_clusters(tmp_project: Path, capsys):
    """Clusters smaller than --min-size should be excluded from output."""
    main([str(tmp_project), "--depth", "1", "--json", "--min-size", "2"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert all(entry["size"] >= 2 for entry in data)


def test_main_no_files_exits(tmp_path: Path):
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(SystemExit):
        main([str(empty)])
