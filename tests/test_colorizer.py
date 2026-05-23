"""Tests for depgraph.colorizer."""

import pytest
from depgraph.colorizer import (
    colorize_by_prefix,
    colorize_by_metric,
    apply_cycle_color,
    _PALETTE,
    _CYCLE_COLOR,
)


# ---------------------------------------------------------------------------
# colorize_by_prefix
# ---------------------------------------------------------------------------

def test_colorize_by_prefix_same_prefix_same_color():
    nodes = ["pkg.a", "pkg.b", "pkg.c"]
    result = colorize_by_prefix(nodes)
    assert result["pkg.a"] == result["pkg.b"] == result["pkg.c"]


def test_colorize_by_prefix_different_prefixes_different_colors():
    nodes = ["alpha.x", "beta.y"]
    result = colorize_by_prefix(nodes)
    assert result["alpha.x"] != result["beta.y"]


def test_colorize_by_prefix_all_nodes_present():
    nodes = ["a.b", "c.d", "e.f"]
    result = colorize_by_prefix(nodes)
    assert set(result.keys()) == set(nodes)


def test_colorize_by_prefix_empty_list():
    assert colorize_by_prefix([]) == {}


def test_colorize_by_prefix_wraps_palette():
    # Create more distinct prefixes than palette entries
    nodes = [f"pkg{i}.mod" for i in range(len(_PALETTE) + 3)]
    result = colorize_by_prefix(nodes)
    # All nodes should have a color (palette wraps)
    assert all(v.startswith("#") for v in result.values())


def test_colorize_by_prefix_no_separator_uses_whole_name():
    nodes = ["alpha", "alpha", "beta"]
    result = colorize_by_prefix(nodes)
    assert result["alpha"] == result["alpha"]
    assert result["alpha"] != result["beta"]


# ---------------------------------------------------------------------------
# colorize_by_metric
# ---------------------------------------------------------------------------

def test_colorize_by_metric_returns_all_nodes():
    nodes = ["a", "b", "c"]
    metrics = {"a": {"in_degree": 3}, "b": {"in_degree": 1}, "c": {"in_degree": 0}}
    result = colorize_by_metric(nodes, metrics)
    assert set(result.keys()) == set(nodes)


def test_colorize_by_metric_high_value_darker():
    nodes = ["a", "b"]
    metrics = {"a": {"in_degree": 10}, "b": {"in_degree": 0}}
    result = colorize_by_metric(nodes, metrics)
    # Node 'b' has in_degree=0 -> intensity=255 -> #ffffffff blue component
    # Node 'a' has max in_degree -> intensity=0 -> #0000ff
    assert result["a"] == "#0000ff"
    assert result["b"] == "#ffffff"


def test_colorize_by_metric_missing_node_treated_as_zero():
    nodes = ["a", "missing"]
    metrics = {"a": {"in_degree": 5}}
    result = colorize_by_metric(nodes, metrics)
    assert "missing" in result
    assert result["missing"].startswith("#")


def test_colorize_by_metric_empty_nodes():
    assert colorize_by_metric([], {}) == {}


# ---------------------------------------------------------------------------
# apply_cycle_color
# ---------------------------------------------------------------------------

def test_apply_cycle_color_overrides_cycle_nodes():
    color_map = {"a": "#aaaaaa", "b": "#bbbbbb", "c": "#cccccc"}
    result = apply_cycle_color(color_map, ["a", "c"])
    assert result["a"] == _CYCLE_COLOR
    assert result["c"] == _CYCLE_COLOR
    assert result["b"] == "#bbbbbb"  # unchanged


def test_apply_cycle_color_does_not_mutate_original():
    color_map = {"a": "#aaaaaa"}
    apply_cycle_color(color_map, ["a"])
    assert color_map["a"] == "#aaaaaa"


def test_apply_cycle_color_empty_cycle_list():
    color_map = {"a": "#aaaaaa"}
    result = apply_cycle_color(color_map, [])
    assert result == color_map
