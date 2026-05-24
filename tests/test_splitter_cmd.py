"""Tests for depgraph.splitter_cmd."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest

from depgraph.splitter_cmd import parse_splitter_args, main


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_project(tmp_path: Path) -> Path:
    (tmp_path / "alpha.py").write_text("import beta\n")
    (tmp_path / "beta.py").write_text("")
    (tmp_path / "gamma.py").write_text("import delta\n")
    (tmp_path / "delta.py").write_text("")
    return tmp_path


# ---------------------------------------------------------------------------
# parse_splitter_args
# ---------------------------------------------------------------------------

def test_parse_splitter_args_defaults(tmp_path):
    args = parse_splitter_args([str(tmp_path)])
    assert args.path == str(tmp_path)
    assert args.format == "text"
    assert args.min_size == 1


def test_parse_splitter_args_custom(tmp_path):
    args = parse_splitter_args([str(tmp_path), "--format", "json", "--min-size", "3"])
    assert args.format == "json"
    assert args.min_size == 3


# ---------------------------------------------------------------------------
# main — text format
# ---------------------------------------------------------------------------

def test_main_text_output_shows_components(tmp_project, capsys):
    main([str(tmp_project)])
    captured = capsys.readouterr().out
    assert "Total components" in captured
    assert "Component" in captured


def test_main_text_output_two_components(tmp_project, capsys):
    main([str(tmp_project)])
    captured = capsys.readouterr().out
    assert "2" in captured  # two components expected


def test_main_min_size_filters(tmp_project, capsys):
    # min-size=10 should exclude all small components
    main([str(tmp_project), "--min-size", "10"])
    captured = capsys.readouterr().out
    assert "Component 1" not in captured


# ---------------------------------------------------------------------------
# main — json format
# ---------------------------------------------------------------------------

def test_main_json_output_is_valid(tmp_project, capsys):
    main([str(tmp_project), "--format", "json"])
    captured = capsys.readouterr().out
    data = json.loads(captured)
    assert isinstance(data, list)


def test_main_json_output_has_required_keys(tmp_project, capsys):
    main([str(tmp_project), "--format", "json"])
    data = json.loads(capsys.readouterr().out)
    for entry in data:
        assert "component" in entry
        assert "nodes" in entry
        assert "graph" in entry


def test_main_json_nodes_are_sorted(tmp_project, capsys):
    main([str(tmp_project), "--format", "json"])
    data = json.loads(capsys.readouterr().out)
    for entry in data:
        assert entry["nodes"] == sorted(entry["nodes"])
