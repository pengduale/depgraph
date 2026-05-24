"""Tests for depgraph.scorer."""

from __future__ import annotations

import pytest

from depgraph.scorer import format_scores, rank_nodes, score_nodes


@pytest.fixture()
def simple_graph() -> dict[str, list[str]]:
    # a -> b -> c
    #      b -> d
    return {
        "a": ["b"],
        "b": ["c", "d"],
        "c": [],
        "d": [],
    }


def test_score_nodes_all_present(simple_graph):
    scores = score_nodes(simple_graph)
    assert set(scores.keys()) == set(simple_graph.keys())


def test_score_nodes_values_in_range(simple_graph):
    scores = score_nodes(simple_graph)
    for v in scores.values():
        assert 0.0 <= v <= 1.0


def test_score_nodes_high_in_degree_scores_higher(simple_graph):
    # 'b' is depended on by 'a' (in-degree 1) and has out-degree 2
    # 'c' and 'd' have in-degree 1, out-degree 0
    scores = score_nodes(simple_graph)
    # b has both in and out degree; should outscore c and d
    assert scores["b"] > scores["c"]
    assert scores["b"] > scores["d"]


def test_score_nodes_empty_graph():
    assert score_nodes({}) == {}


def test_score_nodes_single_node():
    scores = score_nodes({"only": []})
    assert scores == {"only": 0.0}


def test_score_nodes_custom_weights():
    graph = {"a": ["b"], "b": []}
    s_default = score_nodes(graph)
    s_in_heavy = score_nodes(graph, in_weight=1.0, out_weight=0.0)
    # With only in-weight, 'b' (in-degree 1) should score 1.0
    assert s_in_heavy["b"] == 1.0
    assert s_in_heavy["a"] == 0.0


def test_rank_nodes_sorted_descending(simple_graph):
    scores = score_nodes(simple_graph)
    ranked = rank_nodes(scores)
    values = [v for _, v in ranked]
    assert values == sorted(values, reverse=True)


def test_rank_nodes_top_limits_results(simple_graph):
    scores = score_nodes(simple_graph)
    ranked = rank_nodes(scores, top=2)
    assert len(ranked) == 2


def test_rank_nodes_top_none_returns_all(simple_graph):
    scores = score_nodes(simple_graph)
    ranked = rank_nodes(scores)
    assert len(ranked) == len(simple_graph)


def test_rank_nodes_empty():
    assert rank_nodes({}) == []


def test_format_scores_contains_node_names(simple_graph):
    scores = score_nodes(simple_graph)
    ranked = rank_nodes(scores)
    output = format_scores(ranked)
    for node in simple_graph:
        assert node in output


def test_format_scores_empty():
    assert format_scores([]) == "(no nodes)"


def test_format_scores_header_present(simple_graph):
    ranked = rank_nodes(score_nodes(simple_graph))
    output = format_scores(ranked)
    assert "Node" in output
    assert "Score" in output
