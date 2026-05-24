"""Tests for depgraph.matrix."""

import pytest
from depgraph.matrix import build_matrix, matrix_to_graph, format_matrix, density


@pytest.fixture()
def simple_graph():
    return {
        "a": ["b", "c"],
        "b": ["c"],
        "c": [],
    }


def test_build_matrix_nodes_sorted(simple_graph):
    nodes, _ = build_matrix(simple_graph)
    assert nodes == ["a", "b", "c"]


def test_build_matrix_shape(simple_graph):
    nodes, matrix = build_matrix(simple_graph)
    assert len(matrix) == len(nodes)
    assert all(len(row) == len(nodes) for row in matrix)


def test_build_matrix_edges(simple_graph):
    nodes, matrix = build_matrix(simple_graph)
    idx = {n: i for i, n in enumerate(nodes)}
    assert matrix[idx["a"]][idx["b"]] == 1
    assert matrix[idx["a"]][idx["c"]] == 1
    assert matrix[idx["b"]][idx["c"]] == 1
    assert matrix[idx["c"]][idx["a"]] == 0


def test_build_matrix_ignores_unknown_deps():
    graph = {"a": ["external_lib"]}
    nodes, matrix = build_matrix(graph)
    # external_lib not in graph keys — no column for it
    assert nodes == ["a"]
    assert matrix == [[0]]


def test_build_matrix_empty_graph():
    nodes, matrix = build_matrix({})
    assert nodes == []
    assert matrix == []


def test_matrix_to_graph_roundtrip(simple_graph):
    nodes, matrix = build_matrix(simple_graph)
    recovered = matrix_to_graph(nodes, matrix)
    for node in nodes:
        assert sorted(recovered[node]) == sorted(simple_graph[node])


def test_format_matrix_contains_node_names(simple_graph):
    nodes, matrix = build_matrix(simple_graph)
    output = format_matrix(nodes, matrix)
    for n in nodes:
        assert n in output


def test_format_matrix_empty():
    assert format_matrix([], []) == "(empty)"


def test_density_full_graph():
    # 3 nodes, all possible directed edges present (excluding self-loops)
    nodes = ["a", "b", "c"]
    matrix = [
        [0, 1, 1],
        [1, 0, 1],
        [1, 1, 0],
    ]
    assert density(matrix) == pytest.approx(1.0)


def test_density_no_edges():
    matrix = [[0, 0], [0, 0]]
    assert density(matrix) == pytest.approx(0.0)


def test_density_single_node():
    assert density([[0]]) == pytest.approx(0.0)


def test_density_partial(simple_graph):
    _, matrix = build_matrix(simple_graph)
    d = density(matrix)
    # 3 edges out of 6 possible
    assert d == pytest.approx(3 / 6)
