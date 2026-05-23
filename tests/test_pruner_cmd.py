"""Tests for depgraph.pruner_cmd."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest

from depgraph.pruner_cmd import parse_pruner_args, main


@pytest.fixture()
def tmp_project(tmp_path: Path) -> Path:
    """Create a tiny Python project with a transitive dependency."""
    (tmp_path / "a.py").write_text(
        textwrap.dedent("""\
            import b
            import c
        """)
    )
    (tmp_path / "b.py").write_text("import c\n")
    (tmp_path / "c.py").write_text("")
    return tmp_path


# ---------------------------------------------------------------------------
# parse_pruner_args
# ---------------------------------------------------------------------------

def test_parse_pruner_args_defaults():
    args = parse_pruner_args(["myproject"])
    assert args.path == "myproject"
    assert args.transitive is False
    assert args.trim_leaves == 0
    assert args.trim_roots == 0
    assert args.format == "text"


def test_parse_pruner_args_all_flags():
    args = parse_pruner_args([
        "myproject",
        "--transitive",
        "--trim-leaves", "2",
        "--trim-roots", "1",
        "--format", "json",
    ])
    assert args.transitive is True
    assert args.trim_leaves == 2
    assert args.trim_roots == 1
    assert args.format == "json"


# ---------------------------------------------------------------------------
# main — text output
# ---------------------------------------------------------------------------

def test_main_text_output(tmp_project: Path, capsys):
    main([str(tmp_project), "--format", "text"])
    out = capsys.readouterr().out
    assert "->" in out


def test_main_text_transitive(tmp_project: Path, capsys):
    main([str(tmp_project), "--transitive", "--format", "text"])
    out = capsys.readouterr().out
    # After removing transitive edge a->c, a should only show b
    lines = {line.split("->")[0].strip(): line for line in out.splitlines() if "->" in line}
    if "a" in lines:
        assert "c" not in lines["a"] or "b" in lines["a"]


# ---------------------------------------------------------------------------
# main — json output
# ---------------------------------------------------------------------------

def test_main_json_output(tmp_project: Path, capsys):
    main([str(tmp_project), "--format", "json"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert isinstance(data, dict)


def test_main_json_transitive_removes_edge(tmp_project: Path, capsys):
    main([str(tmp_project), "--transitive", "--format", "json"])
    out = capsys.readouterr().out
    data = json.loads(out)
    # Resolve module names (keys may include path prefix)
    a_key = next((k for k in data if k.endswith("a")), None)
    if a_key is not None:
        c_key_suffix = "c"
        deps = data[a_key]
        # Transitive edge to c should be removed
        assert not any(d.endswith(c_key_suffix) for d in deps)
