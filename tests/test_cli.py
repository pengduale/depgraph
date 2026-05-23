"""Tests for the depgraph CLI module."""

import os
from pathlib import Path

import pytest

from depgraph.cli import collect_python_files, main, parse_args


@pytest.fixture
def tmp_project(tmp_path):
    """Create a minimal temporary Python project."""
    (tmp_path / "main.py").write_text("import utils\nimport os\n")
    (tmp_path / "utils.py").write_text("import os\n")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "helper.py").write_text("import utils\n")
    return tmp_path


def test_parse_args_defaults():
    args = parse_args([])
    assert args.path == "."
    assert args.output == "depgraph.svg"
    assert args.exclude == []
    assert args.no_open is False


def test_parse_args_custom():
    args = parse_args(["myproject", "-o", "out.svg", "--exclude", "os", "sys", "--no-open"])
    assert args.path == "myproject"
    assert args.output == "out.svg"
    assert args.exclude == ["os", "sys"]
    assert args.no_open is True


def test_collect_python_files_directory(tmp_project):
    files = collect_python_files(tmp_project)
    names = {f.name for f in files}
    assert "main.py" in names
    assert "utils.py" in names
    assert "helper.py" in names


def test_collect_python_files_single_file(tmp_project):
    single = tmp_project / "main.py"
    files = collect_python_files(single)
    assert len(files) == 1
    assert files[0].name == "main.py"


def test_collect_python_files_empty(tmp_path):
    files = collect_python_files(tmp_path)
    assert files == []


def test_main_generates_svg(tmp_project, tmp_path):
    output = tmp_path / "result.svg"
    result = main([str(tmp_project), "-o", str(output), "--no-open"])
    assert result == 0
    assert output.exists()
    content = output.read_text(encoding="utf-8")
    assert "<svg" in content


def test_main_invalid_path(tmp_path):
    result = main([str(tmp_path / "nonexistent"), "--no-open"])
    assert result == 1


def test_main_no_python_files(tmp_path):
    result = main([str(tmp_path), "--no-open"])
    assert result == 1
