"""Tests for depgraph.weigher."""

import pytest
from depgraph.weigher import (
    weight_by_shared_dependents,
    weight_by_out_degree,
    weight_by_combined,
    normalize_weights,
    format_weights,
)


@pytest.fixture
def simple_graph():
    return {
        "a": ["b", "c"],
        "b": ["c"],
        "c": [],
    }


def test_weight_by_shared_dependents_all_edges_present(simple_graph):
    w = weight_by_shared_dependents(simple_graph)
    assert ("a", "b") in w
    assert ("a", "c") in w
    assert ("b", "c") in w


def test_weight_by_shared_dependents_popular_node(simple_graph):
    # 'c' has in-degree 2, so edges pointing to it should have weight 2
    w = weight_by_shared_dependents(simple_graph)
    assert w[("a", "c")] == 2.0
    assert w[("b", "c")] == 2.0


def test_weight_by_shared_dependents_less_popular_node(simple_graph):
    # 'b' has in-degree 1
    w = weight_by_shared_dependents(simple_graph)
    assert w[("a", "b")] == 1.0


def test_weight_by_out_degree_all_edges_present(simple_graph):
    w = weight_by_out_degree(simple_graph)
    assert ("a", "b") in w
    assert ("a", "c") in w
    assert ("b", "c") in w


def test_weight_by_out_degree_values(simple_graph):
    w = weight_by_out_degree(simple_graph)
    # 'a' has out-degree 2
    assert w[("a", "b")] == 2.0
    assert w[("a", "c")] == 2.0
    # 'b' has out-degree 1
    assert w[("b", "c")] == 1.0


def test_weight_by_combined_alpha_zero_equals_out_degree(simple_graph):
    combined = weight_by_combined(simple_graph, alpha=0.0)
    out_deg = weight_by_out_degree(simple_graph)
    for edge in out_deg:
        assert combined[edge] == pytest.approx(out_deg[edge])


def test_weight_by_combined_alpha_one_equals_shared(simple_graph):
    combined = weight_by_combined(simple_graph, alpha=1.0)
    shared = weight_by_shared_dependents(simple_graph)
    for edge in shared:
        assert combined[edge] == pytest.approx(shared[edge])


def test_weight_by_combined_invalid_alpha(simple_graph):
    with pytest.raises(ValueError):
        weight_by_combined(simple_graph, alpha=1.5)


def test_normalize_weights_max_is_one(simple_graph):
    w = weight_by_shared_dependents(simple_graph)
    n = normalize_weights(w)
    assert max(n.values()) == pytest.approx(1.0)


def test_normalize_weights_empty():
    assert normalize_weights({}) == {}


def test_normalize_weights_all_zero():
    w = {("a", "b"): 0.0, ("b", "c"): 0.0}
    n = normalize_weights(w)
    assert all(v == 0.0 for v in n.values())


def test_format_weights_returns_string(simple_graph):
    w = weight_by_shared_dependents(simple_graph)
    output = format_weights(w)
    assert isinstance(output, str)
    assert "->" in output


def test_format_weights_top_n_limits_output(simple_graph):
    w = weight_by_shared_dependents(simple_graph)
    output = format_weights(w, top_n=1)
    # Only one edge line should appear
    lines = [l for l in output.splitlines() if "->" in l]
    assert len(lines) == 1
