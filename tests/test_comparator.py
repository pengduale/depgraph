"""Tests for depgraph.comparator."""

import pytest

from depgraph.comparator import (
    added_nodes,
    removed_nodes,
    added_edges,
    removed_edges,
    compare_graphs,
    is_identical,
    format_comparison,
)


@pytest.fixture()
def old_graph():
    return {
        "a": ["b", "c"],
        "b": ["c"],
        "c": [],
    }


@pytest.fixture()
def new_graph():
    return {
        "a": ["b"],
        "b": ["c", "d"],
        "c": [],
        "d": [],
    }


def test_added_nodes(old_graph, new_graph):
    assert added_nodes(old_graph, new_graph) == ["d"]


def test_removed_nodes(old_graph, new_graph):
    assert removed_nodes(old_graph, new_graph) == []


def test_removed_nodes_detects_missing(old_graph):
    new = {"a": [], "b": []}
    assert removed_nodes(old_graph, new) == ["c"]


def test_added_edges(old_graph, new_graph):
    assert added_edges(old_graph, new_graph) == [("b", "d")]


def test_removed_edges(old_graph, new_graph):
    assert removed_edges(old_graph, new_graph) == [("a", "c")]


def test_compare_graphs_structure(old_graph, new_graph):
    result = compare_graphs(old_graph, new_graph)
    assert set(result.keys()) == {
        "added_nodes", "removed_nodes", "added_edges", "removed_edges"
    }


def test_is_identical_same_graph(old_graph):
    import copy
    assert is_identical(old_graph, copy.deepcopy(old_graph))


def test_is_identical_different_graphs(old_graph, new_graph):
    assert not is_identical(old_graph, new_graph)


def test_is_identical_empty_graphs():
    assert is_identical({}, {})


def test_format_comparison_contains_labels(old_graph, new_graph):
    result = compare_graphs(old_graph, new_graph)
    text = format_comparison(result)
    assert "Added nodes" in text
    assert "Removed nodes" in text
    assert "Added edges" in text
    assert "Removed edges" in text


def test_format_comparison_lists_edge(old_graph, new_graph):
    result = compare_graphs(old_graph, new_graph)
    text = format_comparison(result)
    assert "b -> d" in text


def test_format_comparison_lists_node():
    old = {"x": []}
    new = {"x": [], "y": []}
    result = compare_graphs(old, new)
    text = format_comparison(result)
    assert "y" in text
