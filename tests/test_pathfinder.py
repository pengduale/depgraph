"""Tests for depgraph.pathfinder."""

import pytest
from depgraph.pathfinder import shortest_path, all_paths, path_exists, format_path


@pytest.fixture
def graph():
    return {
        "a": ["b", "c"],
        "b": ["d"],
        "c": ["d"],
        "d": ["e"],
        "e": [],
        "orphan": [],
    }


def test_shortest_path_direct(graph):
    assert shortest_path(graph, "a", "b") == ["a", "b"]


def test_shortest_path_multi_hop(graph):
    result = shortest_path(graph, "a", "e")
    assert result is not None
    assert result[0] == "a"
    assert result[-1] == "e"
    assert len(result) == 4  # a -> b -> d -> e  or  a -> c -> d -> e


def test_shortest_path_same_node(graph):
    assert shortest_path(graph, "a", "a") == ["a"]


def test_shortest_path_no_path(graph):
    assert shortest_path(graph, "e", "a") is None


def test_shortest_path_missing_source(graph):
    assert shortest_path(graph, "z", "a") is None


def test_shortest_path_missing_target(graph):
    assert shortest_path(graph, "a", "z") is None


def test_all_paths_finds_two_routes(graph):
    paths = all_paths(graph, "a", "d")
    assert len(paths) == 2
    assert ["a", "b", "d"] in paths
    assert ["a", "c", "d"] in paths


def test_all_paths_single_route(graph):
    paths = all_paths(graph, "b", "e")
    assert paths == [["b", "d", "e"]]


def test_all_paths_no_route(graph):
    assert all_paths(graph, "e", "a") == []


def test_all_paths_missing_node(graph):
    assert all_paths(graph, "a", "missing") == []


def test_all_paths_max_depth_limits(graph):
    # max_depth=1 means only direct neighbours
    paths = all_paths(graph, "a", "d", max_depth=1)
    assert paths == []


def test_path_exists_true(graph):
    assert path_exists(graph, "a", "e") is True


def test_path_exists_false(graph):
    assert path_exists(graph, "e", "a") is False


def test_path_exists_orphan(graph):
    assert path_exists(graph, "orphan", "a") is False


def test_format_path_basic():
    assert format_path(["a", "b", "c"]) == "a -> b -> c"


def test_format_path_single_node():
    assert format_path(["a"]) == "a"
