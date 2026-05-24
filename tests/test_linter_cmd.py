"""Tests for depgraph.linter_cmd."""
from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest

from depgraph.linter_cmd import main, parse_linter_args


@pytest.fixture()
def tmp_project(tmp_path: Path) -> Path:
    (tmp_path / "a.py").write_text("import b\n")
    (tmp_path / "b.py").write_text("import a\n")  # creates a cycle a <-> b
    return tmp_path


def test_parse_linter_args_defaults(tmp_path):
    args = parse_linter_args([str(tmp_path)])
    assert args.path == str(tmp_path)
    assert args.format == "text"
    assert args.exit_code is False
    assert args.only is None


def test_parse_linter_args_custom(tmp_path):
    args = parse_linter_args([
        str(tmp_path),
        "--format", "json",
        "--exit-code",
        "--only", "E001", "W001",
    ])
    assert args.format == "json"
    assert args.exit_code is True
    assert args.only == ["E001", "W001"]


def test_main_text_output_no_issues(tmp_path, capsys):
    (tmp_path / "clean.py").write_text("x = 1\n")
    main([str(tmp_path)])
    captured = capsys.readouterr()
    assert "No issues found" in captured.out


def test_main_text_output_with_cycle(tmp_project, capsys):
    main([str(tmp_project)])
    captured = capsys.readouterr()
    assert "E001" in captured.out or "Cycle" in captured.out


def test_main_json_output(tmp_project, capsys):
    main([str(tmp_project), "--format", "json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert isinstance(data, list)
    if data:
        assert "code" in data[0]
        assert "message" in data[0]
        assert "nodes" in data[0]


def test_main_exit_code_zero_no_issues(tmp_path):
    (tmp_path / "ok.py").write_text("")
    # Should not raise SystemExit
    main([str(tmp_path), "--exit-code"])


def test_main_exit_code_one_with_issues(tmp_project):
    with pytest.raises(SystemExit) as exc_info:
        main([str(tmp_project), "--exit-code"])
    assert exc_info.value.code == 1


def test_main_only_filter(tmp_project, capsys):
    main([str(tmp_project), "--only", "W001"])
    captured = capsys.readouterr()
    # E001 cycles should be filtered out; only W001 (or no issues) shown
    assert "E001" not in captured.out
