"""Tests for depgraph.filter module."""

import pytest
from depgraph.filter import (
    filter_by_prefix,
    filter_by_depth,
    exclude_nodes,
    remove_isolated_nodes,
)


SAMPLE_GRAPH = {
    "pkg.a": {"pkg.b", "pkg.c"},
    "pkg.b": {"pkg.c"},
    "pkg.c": set(),
    "other.x": {"pkg.a"},
    "other.y": set(),
}


def test_filter_by_prefix_keeps_matching_nodes():
    result = filter_by_prefix(SAMPLE_GRAPH, "pkg.")
    assert set(result.keys()) == {"pkg.a", "pkg.b", "pkg.c"}


def test_filter_by_prefix_removes_cross_prefix_edges():
    result = filter_by_prefix(SAMPLE_GRAPH, "pkg.")
    assert "other.x" not in result.get("pkg.a", set())


def test_filter_by_prefix_no_match_returns_empty():
    result = filter_by_prefix(SAMPLE_GRAPH, "nonexistent.")
    assert result == {}


def test_filter_by_depth_direct_deps():
    graph = {"a": {"b", "c"}, "b": {"d"}, "c": set(), "d": set()}
    result = filter_by_depth(graph, "a", max_depth=1)
    assert "a" in result
    assert "b" in result
    assert "c" in result
    assert "d" not in result


def test_filter_by_depth_full_reach():
    graph = {"a": {"b"}, "b": {"c"}, "c": set()}
    result = filter_by_depth(graph, "a", max_depth=2)
    assert set(result.keys()) == {"a", "b", "c"}


def test_filter_by_depth_unknown_root_returns_empty():
    result = filter_by_depth(SAMPLE_GRAPH, "unknown", max_depth=5)
    assert result == {}


def test_exclude_nodes_removes_node_and_edges():
    result = exclude_nodes(SAMPLE_GRAPH, ["pkg.c"])
    assert "pkg.c" not in result
    assert "pkg.c" not in result.get("pkg.a", set())
    assert "pkg.c" not in result.get("pkg.b", set())


def test_exclude_nodes_multiple():
    result = exclude_nodes(SAMPLE_GRAPH, ["pkg.b", "other.x"])
    assert "pkg.b" not in result
    assert "other.x" not in result


def test_exclude_nodes_empty_list_unchanged():
    result = exclude_nodes(SAMPLE_GRAPH, [])
    assert result.keys() == SAMPLE_GRAPH.keys()


def test_remove_isolated_nodes_removes_no_edge_nodes():
    graph = {"a": {"b"}, "b": set(), "c": set()}
    result = remove_isolated_nodes(graph)
    assert "c" not in result
    assert "a" in result
    assert "b" in result


def test_remove_isolated_nodes_all_connected():
    graph = {"a": {"b"}, "b": {"a"}}
    result = remove_isolated_nodes(graph)
    assert set(result.keys()) == {"a", "b"}
