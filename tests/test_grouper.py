"""Tests for depgraph.grouper module."""

import pytest
from depgraph.grouper import group_by_prefix, group_by_mapping, inter_group_edges


# ---------------------------------------------------------------------------
# group_by_prefix
# ---------------------------------------------------------------------------

def test_group_by_prefix_single_depth():
    nodes = ["a.b", "a.c", "b.d", "b.e"]
    groups = group_by_prefix(nodes, depth=1)
    assert set(groups["a"]) == {"a.b", "a.c"}
    assert set(groups["b"]) == {"b.d", "b.e"}


def test_group_by_prefix_depth_two():
    nodes = ["a.b.c", "a.b.d", "a.x.y"]
    groups = group_by_prefix(nodes, depth=2)
    assert set(groups["a.b"]) == {"a.b.c", "a.b.d"}
    assert set(groups["a.x"]) == {"a.x.y"}


def test_group_by_prefix_no_dot():
    nodes = ["foo", "bar", "baz"]
    groups = group_by_prefix(nodes, depth=1)
    assert groups["foo"] == ["foo"]
    assert groups["bar"] == ["bar"]
    assert groups["baz"] == ["baz"]


def test_group_by_prefix_empty():
    assert group_by_prefix([], depth=1) == {}


def test_group_by_prefix_depth_exceeds_parts():
    # depth larger than available parts should just use the whole name
    nodes = ["a.b", "a.b"]
    groups = group_by_prefix(nodes, depth=5)
    assert groups["a.b"] == ["a.b", "a.b"]


# ---------------------------------------------------------------------------
# group_by_mapping
# ---------------------------------------------------------------------------

def test_group_by_mapping_basic():
    nodes = ["a", "b", "c"]
    mapping = {"a": "group1", "b": "group1", "c": "group2"}
    groups = group_by_mapping(nodes, mapping)
    assert set(groups["group1"]) == {"a", "b"}
    assert groups["group2"] == ["c"]


def test_group_by_mapping_ungrouped():
    nodes = ["a", "b", "unknown"]
    mapping = {"a": "g1", "b": "g1"}
    groups = group_by_mapping(nodes, mapping)
    assert groups["__ungrouped__"] == ["unknown"]


def test_group_by_mapping_empty_nodes():
    assert group_by_mapping([], {"a": "g"}) == {}


def test_group_by_mapping_empty_mapping():
    nodes = ["x", "y"]
    groups = group_by_mapping(nodes, {})
    assert set(groups["__ungrouped__"]) == {"x", "y"}


# ---------------------------------------------------------------------------
# inter_group_edges
# ---------------------------------------------------------------------------

def test_inter_group_edges_basic():
    graph = {"a.b": ["c.d"], "a.c": ["a.b"]}
    groups = group_by_prefix(list(graph.keys()) + ["c.d"], depth=1)
    edges = inter_group_edges(graph, groups)
    assert ("a", "c") in edges


def test_inter_group_edges_no_cross_edges():
    graph = {"a.b": ["a.c"], "a.c": []}
    groups = group_by_prefix(["a.b", "a.c"], depth=1)
    edges = inter_group_edges(graph, groups)
    assert edges == []


def test_inter_group_edges_deduplicates():
    graph = {"a.b": ["b.c"], "a.d": ["b.c"]}
    groups = group_by_prefix(["a.b", "a.d", "b.c"], depth=1)
    edges = inter_group_edges(graph, groups)
    assert edges.count(("a", "b")) == 1


def test_inter_group_edges_unknown_node_skipped():
    graph = {"a.b": ["z.unknown"]}
    groups = group_by_prefix(["a.b"], depth=1)
    # z.unknown is not in groups, should be skipped gracefully
    edges = inter_group_edges(graph, groups)
    assert edges == []
