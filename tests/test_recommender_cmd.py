"""Tests for depgraph.recommender_cmd."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest

from depgraph.recommender_cmd import main, parse_recommender_args


# ---------------------------------------------------------------------------
# Fixture — tiny project on disk
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_project(tmp_path: Path) -> Path:
    (tmp_path / "a.py").write_text("import b\nimport c\n")
    (tmp_path / "b.py").write_text("import a\n")  # cycle a <-> b
    (tmp_path / "c.py").write_text("")             # isolated leaf
    return tmp_path


# ---------------------------------------------------------------------------
# parse_recommender_args
# ---------------------------------------------------------------------------

def test_parse_recommender_args_defaults():
    args = parse_recommender_args(["myproject"])
    assert args.path == "myproject"
    assert args.coupling_threshold == 5
    assert args.god_threshold == 5
    assert args.format == "text"
    assert args.severity is None


def test_parse_recommender_args_custom():
    args = parse_recommender_args([
        "myproject",
        "--coupling-threshold", "3",
        "--god-threshold", "2",
        "--format", "json",
        "--severity", "error",
    ])
    assert args.coupling_threshold == 3
    assert args.god_threshold == 2
    assert args.format == "json"
    assert args.severity == "error"


# ---------------------------------------------------------------------------
# main — text output
# ---------------------------------------------------------------------------

def test_main_text_output_contains_cycle(tmp_project, capsys):
    with pytest.raises(SystemExit) as exc_info:
        main([str(tmp_project)])
    captured = capsys.readouterr()
    assert "cycle" in captured.out.lower()
    assert exc_info.value.code == 1  # errors present


def test_main_text_healthy(tmp_path, capsys):
    (tmp_path / "x.py").write_text("")
    with pytest.raises(SystemExit) as exc_info:
        main([str(tmp_path)])
    captured = capsys.readouterr()
    # isolated node 'x' -> info only, exit 0
    assert exc_info.value.code == 0


# ---------------------------------------------------------------------------
# main — JSON output
# ---------------------------------------------------------------------------

def test_main_json_output_is_valid(tmp_project, capsys):
    with pytest.raises(SystemExit):
        main([str(tmp_project), "--format", "json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert isinstance(data, list)


def test_main_json_output_has_required_keys(tmp_project, capsys):
    with pytest.raises(SystemExit):
        main([str(tmp_project), "--format", "json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    for item in data:
        assert "node" in item
        assert "category" in item
        assert "severity" in item
        assert "message" in item


# ---------------------------------------------------------------------------
# main — severity filter
# ---------------------------------------------------------------------------

def test_main_severity_filter_error_only(tmp_project, capsys):
    with pytest.raises(SystemExit):
        main([str(tmp_project), "--format", "json", "--severity", "error"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert all(item["severity"] == "error" for item in data)


def test_main_severity_filter_info_only(tmp_project, capsys):
    with pytest.raises(SystemExit):
        main([str(tmp_project), "--format", "json", "--severity", "info"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert all(item["severity"] == "info" for item in data)
