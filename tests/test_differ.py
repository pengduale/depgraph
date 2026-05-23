"""Tests for depgraph.differ."""

import pytest
from depgraph.differ import diff_graphs, is_empty_diff, format_diff


@pytest.fixture
def base_graph():
    return {
        "a": {"b", "c"},
        "b": {"c"},
        "c": set(),
    }


def test_no_changes(base_graph):
    diff = diff_graphs(base_graph, base_graph)
    assert diff["added_nodes"] == []
    assert diff["removed_nodes"] == []
    assert diff["added_edges"] == []
    assert diff["removed_edges"] == []


def test_added_node(base_graph):
    new = dict(base_graph)
    new["d"] = set()
    diff = diff_graphs(base_graph, new)
    assert "d" in diff["added_nodes"]
    assert diff["removed_nodes"] == []


def test_removed_node(base_graph):
    new = {k: v for k, v in base_graph.items() if k != "b"}
    diff = diff_graphs(base_graph, new)
    assert "b" in diff["removed_nodes"]
    assert diff["added_nodes"] == []


def test_added_edge(base_graph):
    import copy
    new = copy.deepcopy(base_graph)
    new["c"].add("a")
    diff = diff_graphs(base_graph, new)
    assert ("c", "a") in diff["added_edges"]
    assert diff["removed_edges"] == []


def test_removed_edge(base_graph):
    import copy
    new = copy.deepcopy(base_graph)
    new["a"].discard("c")
    diff = diff_graphs(base_graph, new)
    assert ("a", "c") in diff["removed_edges"]
    assert diff["added_edges"] == []


def test_empty_to_populated():
    diff = diff_graphs({}, {"x": {"y"}, "y": set()})
    assert set(diff["added_nodes"]) == {"x", "y"}
    assert ("x", "y") in diff["added_edges"]


def test_is_empty_diff_true(base_graph):
    diff = diff_graphs(base_graph, base_graph)
    assert is_empty_diff(diff) is True


def test_is_empty_diff_false(base_graph):
    import copy
    new = copy.deepcopy(base_graph)
    new["z"] = set()
    diff = diff_graphs(base_graph, new)
    assert is_empty_diff(diff) is False


def test_format_diff_no_changes(base_graph):
    diff = diff_graphs(base_graph, base_graph)
    assert format_diff(diff) == "No changes detected."


def test_format_diff_shows_added_node(base_graph):
    new = dict(base_graph)
    new["d"] = set()
    diff = diff_graphs(base_graph, new)
    output = format_diff(diff)
    assert "Added nodes" in output
    assert "+ d" in output


def test_format_diff_shows_removed_edge(base_graph):
    import copy
    new = copy.deepcopy(base_graph)
    new["b"].discard("c")
    diff = diff_graphs(base_graph, new)
    output = format_diff(diff)
    assert "Removed edges" in output
    assert "b -> c" in output
