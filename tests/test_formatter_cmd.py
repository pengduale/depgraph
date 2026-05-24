"""Tests for depgraph.formatter_cmd."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from depgraph.formatter_cmd import main, parse_formatter_args


@pytest.fixture()
def tmp_project(tmp_path: Path) -> Path:
    (tmp_path / "a.py").write_text("import b\n")
    (tmp_path / "b.py").write_text("import c\n")
    (tmp_path / "c.py").write_text("")  # no imports
    return tmp_path


def test_parse_formatter_args_defaults(tmp_project):
    args = parse_formatter_args([str(tmp_project)])
    assert args.style == "adjacency"
    assert args.prefix is None


def test_parse_formatter_args_style_table(tmp_project):
    args = parse_formatter_args([str(tmp_project), "--style", "table"])
    assert args.style == "table"


def test_parse_formatter_args_prefix(tmp_project):
    args = parse_formatter_args([str(tmp_project), "--prefix", "my"])
    assert args.prefix == "my"


def test_main_adjacency_output(tmp_project, capsys):
    main([str(tmp_project), "--style", "adjacency"])
    out = capsys.readouterr().out
    assert "Adjacency list" in out


def test_main_edges_output(tmp_project, capsys):
    main([str(tmp_project), "--style", "edges"])
    out = capsys.readouterr().out
    assert "Edge list" in out


def test_main_table_output(tmp_project, capsys):
    main([str(tmp_project), "--style", "table"])
    out = capsys.readouterr().out
    # table has header or 'No edges'
    assert ("Source" in out) or ("No edges" in out)


def test_main_prefix_filters_nodes(tmp_project, capsys):
    # prefix that matches nothing → empty-ish output
    main([str(tmp_project), "--prefix", "zzz"])
    out = capsys.readouterr().out
    assert "zzz" not in out
