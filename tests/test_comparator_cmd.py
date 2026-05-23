"""Tests for depgraph.comparator_cmd."""

import json
import pytest

from depgraph.snapshot import save_snapshot
from depgraph.comparator_cmd import parse_compare_args, main


@pytest.fixture()
def snapshots(tmp_path):
    old = {"a": ["b", "c"], "b": ["c"], "c": []}
    new = {"a": ["b"], "b": ["c", "d"], "c": [], "d": []}
    old_path = str(tmp_path / "old.json")
    new_path = str(tmp_path / "new.json")
    save_snapshot(old, old_path)
    save_snapshot(new, new_path)
    return old_path, new_path


def test_parse_compare_args_defaults(snapshots):
    old_path, new_path = snapshots
    args = parse_compare_args([old_path, new_path])
    assert args.old == old_path
    assert args.new == new_path
    assert args.format == "text"
    assert args.exit_code is False


def test_parse_compare_args_json_format(snapshots):
    old_path, new_path = snapshots
    args = parse_compare_args([old_path, new_path, "--format", "json"])
    assert args.format == "json"


def test_parse_compare_args_exit_code(snapshots):
    old_path, new_path = snapshots
    args = parse_compare_args([old_path, new_path, "--exit-code"])
    assert args.exit_code is True


def test_main_text_output_differs(snapshots, capsys):
    old_path, new_path = snapshots
    main([old_path, new_path])
    captured = capsys.readouterr()
    assert "Added nodes" in captured.out
    assert "Removed edges" in captured.out


def test_main_text_output_identical(tmp_path, capsys):
    graph = {"a": ["b"], "b": []}
    p1 = str(tmp_path / "g1.json")
    p2 = str(tmp_path / "g2.json")
    save_snapshot(graph, p1)
    save_snapshot(graph, p2)
    main([p1, p2])
    captured = capsys.readouterr()
    assert "identical" in captured.out.lower()


def test_main_json_output(snapshots, capsys):
    old_path, new_path = snapshots
    main([old_path, new_path, "--format", "json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "added_nodes" in data
    assert "removed_edges" in data


def test_main_exit_code_differs(snapshots):
    old_path, new_path = snapshots
    with pytest.raises(SystemExit) as exc_info:
        main([old_path, new_path, "--exit-code"])
    assert exc_info.value.code == 1


def test_main_no_exit_code_when_identical(tmp_path):
    graph = {"a": ["b"], "b": []}
    p1 = str(tmp_path / "g1.json")
    p2 = str(tmp_path / "g2.json")
    save_snapshot(graph, p1)
    save_snapshot(graph, p2)
    # Should not raise
    main([p1, p2, "--exit-code"])
