"""Tests for depgraph.splitter."""

from __future__ import annotations

import pytest

from depgraph.splitter import (
    split_components,
    largest_component,
    component_count,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def two_component_graph():
    return {
        "a": ["b"],
        "b": [],
        "c": ["d"],
        "d": [],
    }


@pytest.fixture()
def single_component_graph():
    return {
        "a": ["b"],
        "b": ["c"],
        "c": [],
    }


# ---------------------------------------------------------------------------
# split_components
# ---------------------------------------------------------------------------

def test_split_components_empty_graph():
    assert split_components({}) == []


def test_split_components_single_node():
    result = split_components({"a": []})
    assert len(result) == 1
    assert "a" in result[0]


def test_split_components_two_components(two_component_graph):
    result = split_components(two_component_graph)
    assert len(result) == 2
    node_sets = [frozenset(c.keys()) for c in result]
    assert frozenset({"a", "b"}) in node_sets
    assert frozenset({"c", "d"}) in node_sets


def test_split_components_single_component(single_component_graph):
    result = split_components(single_component_graph)
    assert len(result) == 1
    assert set(result[0].keys()) == {"a", "b", "c"}


def test_split_components_edges_preserved(two_component_graph):
    result = split_components(two_component_graph)
    merged = {}
    for comp in result:
        merged.update(comp)
    assert merged["a"] == ["b"]
    assert merged["c"] == ["d"]


def test_split_components_no_cross_edges():
    graph = {"a": ["b"], "c": ["d"], "b": [], "d": []}
    for comp in split_components(graph):
        for node, deps in comp.items():
            for dep in deps:
                assert dep in comp, "cross-component edge found"


def test_split_components_isolated_nodes():
    graph = {"a": [], "b": [], "c": []}
    result = split_components(graph)
    assert len(result) == 3


# ---------------------------------------------------------------------------
# largest_component
# ---------------------------------------------------------------------------

def test_largest_component_returns_biggest(two_component_graph):
    # make one component larger
    two_component_graph["e"] = ["c"]
    lc = largest_component(two_component_graph)
    assert set(lc.keys()) == {"c", "d", "e"}


def test_largest_component_empty_graph():
    assert largest_component({}) == {}


# ---------------------------------------------------------------------------
# component_count
# ---------------------------------------------------------------------------

def test_component_count_two(two_component_graph):
    assert component_count(two_component_graph) == 2


def test_component_count_one(single_component_graph):
    assert component_count(single_component_graph) == 1


def test_component_count_empty():
    assert component_count({}) == 0
