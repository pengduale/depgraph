"""Tests for depgraph.tracer."""

import pytest
from depgraph.tracer import (
    chain_summary,
    format_chain,
    trace_all_chains,
    trace_chain,
)


@pytest.fixture
def graph():
    return {
        "a": ["b", "c"],
        "b": ["d"],
        "c": ["d"],
        "d": ["e"],
        "e": [],
        "isolated": [],
    }


def test_trace_chain_direct(graph):
    assert trace_chain(graph, "a", "b") == ["a", "b"]


def test_trace_chain_multi_hop(graph):
    result = trace_chain(graph, "a", "d")
    assert result is not None
    assert result[0] == "a"
    assert result[-1] == "d"
    assert len(result) == 3  # shortest: a -> b -> d or a -> c -> d


def test_trace_chain_same_node(graph):
    assert trace_chain(graph, "a", "a") == ["a"]


def test_trace_chain_no_path(graph):
    assert trace_chain(graph, "e", "a") is None


def test_trace_chain_unknown_source(graph):
    assert trace_chain(graph, "z", "a") is None


def test_trace_chain_to_isolated(graph):
    assert trace_chain(graph, "a", "isolated") is None


def test_trace_all_chains_two_paths(graph):
    chains = trace_all_chains(graph, "a", "d")
    assert len(chains) == 2
    paths = {tuple(c) for c in chains}
    assert ("a", "b", "d") in paths
    assert ("a", "c", "d") in paths


def test_trace_all_chains_single_path(graph):
    chains = trace_all_chains(graph, "b", "e")
    assert chains == [["b", "d", "e"]]


def test_trace_all_chains_no_path(graph):
    assert trace_all_chains(graph, "e", "a") == []


def test_trace_all_chains_same_node(graph):
    assert trace_all_chains(graph, "a", "a") == [["a"]]


def test_trace_all_chains_unknown_source(graph):
    assert trace_all_chains(graph, "z", "a") == []


def test_format_chain_simple():
    assert format_chain(["a", "b", "c"]) == "a -> b -> c"


def test_format_chain_single():
    assert format_chain(["a"]) == "a"


def test_chain_summary_reachable(graph):
    summary = chain_summary(graph, "a", "e")
    assert summary["reachable"] is True
    assert summary["source"] == "a"
    assert summary["target"] == "e"
    assert summary["shortest"] is not None
    assert summary["shortest_length"] == len(summary["shortest"]) - 1
    assert summary["chain_count"] >= 1


def test_chain_summary_unreachable(graph):
    summary = chain_summary(graph, "e", "a")
    assert summary["reachable"] is False
    assert summary["shortest"] is None
    assert summary["shortest_length"] is None
    assert summary["chain_count"] == 0
