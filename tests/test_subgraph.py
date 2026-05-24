"""Tests for depgraph.subgraph."""
import pytest
from depgraph.subgraph import extract_subgraph, neighborhood, induced_subgraph, merge_graphs


@pytest.fixture
def graph():
    return {
        "a": ["b", "c"],
        "b": ["d"],
        "c": ["d"],
        "d": [],
        "e": ["a"],
    }


def test_extract_subgraph_keeps_specified_nodes(graph):
    sub = extract_subgraph(graph, ["a", "b", "d"])
    assert set(sub.keys()) == {"a", "b", "d"}


def test_extract_subgraph_removes_cross_edges(graph):
    sub = extract_subgraph(graph, ["a", "b"])
    # c is not in subgraph, so a->c should be dropped
    assert "c" not in sub["a"]
    assert "b" in sub["a"]


def test_extract_subgraph_unknown_node_gets_empty_deps(graph):
    sub = extract_subgraph(graph, ["a", "z"])
    assert sub["z"] == []


def test_extract_subgraph_empty_node_list(graph):
    sub = extract_subgraph(graph, [])
    assert sub == {}


def test_neighborhood_radius_1(graph):
    sub = neighborhood(graph, "b", radius=1)
    # b -> d (forward), e -> a -> b (reverse one hop: a)
    assert "b" in sub
    assert "d" in sub
    assert "a" in sub  # reverse neighbour


def test_neighborhood_radius_0(graph):
    sub = neighborhood(graph, "b", radius=0)
    assert "b" in sub


def test_neighborhood_unknown_node(graph):
    sub = neighborhood(graph, "z", radius=1)
    assert sub == {}


def test_neighborhood_edges_stay_within_subgraph(graph):
    sub = neighborhood(graph, "b", radius=1)
    for node, deps in sub.items():
        for dep in deps:
            assert dep in sub, f"Edge {node}->{dep} references node outside subgraph"


def test_induced_subgraph_by_predicate(graph):
    sub = induced_subgraph(graph, lambda n: n in {"a", "b", "d"})
    assert set(sub.keys()) == {"a", "b", "d"}
    assert "c" not in sub.get("a", [])


def test_induced_subgraph_no_match(graph):
    sub = induced_subgraph(graph, lambda n: False)
    assert sub == {}


def test_merge_graphs_combines_nodes():
    g1 = {"a": ["b"], "b": []}
    g2 = {"b": ["c"], "c": []}
    merged = merge_graphs(g1, g2)
    assert set(merged.keys()) == {"a", "b", "c"}
    assert "b" in merged["a"]
    assert "c" in merged["b"]


def test_merge_graphs_no_duplicate_edges():
    g1 = {"a": ["b"]}
    g2 = {"a": ["b", "c"]}
    merged = merge_graphs(g1, g2)
    assert merged["a"].count("b") == 1
    assert "c" in merged["a"]


def test_merge_graphs_empty():
    merged = merge_graphs({}, {})
    assert merged == {}
