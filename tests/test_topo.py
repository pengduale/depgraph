"""Tests for depgraph.topo and depgraph.topo_cmd."""

import json
import pytest

from depgraph.topo import topological_sort, assign_layers, layers_to_groups
from depgraph.topo_cmd import main


# ---------------------------------------------------------------------------
# topological_sort
# ---------------------------------------------------------------------------

def test_topological_sort_simple():
    graph = {"a": ["b"], "b": ["c"], "c": []}
    order = topological_sort(graph)
    assert order is not None
    assert order.index("a") < order.index("b") < order.index("c")


def test_topological_sort_empty():
    assert topological_sort({}) == []


def test_topological_sort_cycle_returns_none():
    graph = {"a": ["b"], "b": ["a"]}
    assert topological_sort(graph) is None


def test_topological_sort_self_loop_returns_none():
    graph = {"a": ["a"]}
    assert topological_sort(graph) is None


def test_topological_sort_disconnected():
    graph = {"a": [], "b": [], "c": []}
    order = topological_sort(graph)
    assert order is not None
    assert set(order) == {"a", "b", "c"}


# ---------------------------------------------------------------------------
# assign_layers
# ---------------------------------------------------------------------------

def test_assign_layers_linear():
    graph = {"a": ["b"], "b": ["c"], "c": []}
    layers = assign_layers(graph)
    assert layers == {"a": 0, "b": 1, "c": 2}


def test_assign_layers_diamond():
    graph = {"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []}
    layers = assign_layers(graph)
    assert layers["a"] == 0
    assert layers["d"] == 2
    assert layers["b"] == layers["c"] == 1


def test_assign_layers_cycle_returns_none():
    graph = {"x": ["y"], "y": ["x"]}
    assert assign_layers(graph) is None


# ---------------------------------------------------------------------------
# layers_to_groups
# ---------------------------------------------------------------------------

def test_layers_to_groups_basic():
    layer_map = {"a": 0, "b": 1, "c": 1, "d": 2}
    groups = layers_to_groups(layer_map)
    assert groups[0] == ["a"]
    assert groups[1] == ["b", "c"]
    assert groups[2] == ["d"]


# ---------------------------------------------------------------------------
# topo_cmd.main
# ---------------------------------------------------------------------------

def test_main_order_text(tmp_path, capsys):
    f = tmp_path / "mod.py"
    f.write_text("import os\n")
    ret = main([str(tmp_path), "--mode", "order", "--format", "text"])
    assert ret == 0
    out = capsys.readouterr().out
    assert "mod" in out


def test_main_layers_json(tmp_path, capsys):
    f = tmp_path / "mod.py"
    f.write_text("")
    ret = main([str(tmp_path), "--mode", "layers", "--format", "json"])
    assert ret == 0
    data = json.loads(capsys.readouterr().out)
    assert isinstance(data, dict)
