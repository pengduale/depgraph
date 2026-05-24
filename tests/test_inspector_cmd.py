"""Tests for depgraph.inspector_cmd."""
import json
import os
import textwrap

import pytest

from depgraph.inspector_cmd import main, parse_inspector_args


@pytest.fixture
def tmp_project(tmp_path):
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "__init__.py").write_text("")
    (tmp_path / "pkg" / "a.py").write_text(
        textwrap.dedent("""\
            from pkg import b
            from pkg import c
        """)
    )
    (tmp_path / "pkg" / "b.py").write_text("from pkg import c\n")
    (tmp_path / "pkg" / "c.py").write_text("")
    return tmp_path


def test_parse_inspector_args_defaults(tmp_project):
    args = parse_inspector_args([str(tmp_project)])
    assert args.fmt == "text"
    assert args.node is None
    assert args.edge is None
    assert args.bottlenecks is None


def test_parse_inspector_args_node_flag(tmp_project):
    args = parse_inspector_args([str(tmp_project), "--node", "pkg.a"])
    assert args.node == "pkg.a"


def test_parse_inspector_args_json_format(tmp_project):
    args = parse_inspector_args([str(tmp_project), "--node", "x", "--format", "json"])
    assert args.fmt == "json"


def test_main_node_text_output(tmp_project, capsys):
    main([str(tmp_project), "--node", "pkg.c"])
    out = capsys.readouterr().out
    assert "pkg.c" in out


def test_main_node_json_output(tmp_project, capsys):
    main([str(tmp_project), "--node", "pkg.c", "--format", "json"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["node"] == "pkg.c"
    assert "in_degree" in data


def test_main_edge_text_output(tmp_project, capsys):
    main([str(tmp_project), "--edge", "pkg.b:pkg.c"])
    out = capsys.readouterr().out
    assert "exists" in out


def test_main_edge_json_output(tmp_project, capsys):
    main([str(tmp_project), "--edge", "pkg.b:pkg.c", "--format", "json"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["exists"] is True


def test_main_bottlenecks_text(tmp_project, capsys):
    main([str(tmp_project), "--bottlenecks", "1"])
    out = capsys.readouterr().out
    assert out.strip() != ""


def test_main_bottlenecks_json(tmp_project, capsys):
    main([str(tmp_project), "--bottlenecks", "1", "--format", "json"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert isinstance(data, list)


def test_main_no_flags_exits(tmp_project):
    with pytest.raises(SystemExit):
        main([str(tmp_project)])


def test_main_bad_edge_format_exits(tmp_project):
    with pytest.raises(SystemExit):
        main([str(tmp_project), "--edge", "nodestformat"])
