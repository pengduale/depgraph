"""Tests for depgraph.stats — compute_stats and format_stats."""

import pytest
from depgraph.stats import compute_stats, format_stats


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def simple_graph():
    return {
        "a": ["b", "c"],
        "b": ["c"],
        "c": [],
    }


@pytest.fixture()
def isolated_graph():
    """Graph where 'd' is completely isolated."""
    return {
        "a": ["b"],
        "b": [],
        "c": [],  # isolated
    }


# ---------------------------------------------------------------------------
# compute_stats
# ---------------------------------------------------------------------------

def test_empty_graph_returns_zeros():
    stats = compute_stats({})
    assert stats["node_count"] == 0
    assert stats["edge_count"] == 0
    assert stats["density"] == 0.0
    assert stats["isolated_count"] == 0


def test_node_count(simple_graph):
    assert compute_stats(simple_graph)["node_count"] == 3


def test_edge_count(simple_graph):
    # a->b, a->c, b->c  =>  3 edges
    assert compute_stats(simple_graph)["edge_count"] == 3


def test_avg_out_degree(simple_graph):
    # (2 + 1 + 0) / 3 = 1.0
    assert compute_stats(simple_graph)["avg_out_degree"] == 1.0


def test_avg_in_degree(simple_graph):
    # in: a=0, b=1, c=2  =>  avg = 1.0
    assert compute_stats(simple_graph)["avg_in_degree"] == 1.0


def test_max_out_degree(simple_graph):
    assert compute_stats(simple_graph)["max_out_degree"] == 2


def test_max_in_degree(simple_graph):
    assert compute_stats(simple_graph)["max_in_degree"] == 2


def test_isolated_count(isolated_graph):
    # 'c' has no in or out edges
    assert compute_stats(isolated_graph)["isolated_count"] == 1


def test_no_isolated_nodes(simple_graph):
    # 'c' has in-degree 2, so not isolated
    assert compute_stats(simple_graph)["isolated_count"] == 0


def test_density_simple_graph(simple_graph):
    # 3 edges / (3*2) = 0.5
    assert compute_stats(simple_graph)["density"] == pytest.approx(0.5)


def test_single_node_density():
    stats = compute_stats({"a": []})
    assert stats["density"] == 0.0
    assert stats["isolated_count"] == 1


# ---------------------------------------------------------------------------
# format_stats
# ---------------------------------------------------------------------------

def test_format_stats_contains_all_keys(simple_graph):
    stats = compute_stats(simple_graph)
    output = format_stats(stats)
    for keyword in ("Nodes", "Edges", "out-degree", "in-degree", "Isolated", "density"):
        assert keyword in output


def test_format_stats_shows_values(simple_graph):
    stats = compute_stats(simple_graph)
    output = format_stats(stats)
    assert "3" in output   # node_count
    assert "0.5" in output  # density
