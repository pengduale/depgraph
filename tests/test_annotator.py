"""Tests for depgraph.annotator."""

from __future__ import annotations

import pytest

from depgraph.annotator import (
    annotate_nodes,
    filter_by_annotation,
    LABEL_CYCLE,
    LABEL_ENTRY,
    LABEL_LEAF,
    LABEL_ISOLATED,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def linear_graph():
    """a -> b -> c  (a is entry, c is leaf)"""
    return {"a": ["b"], "b": ["c"], "c": []}


@pytest.fixture()
def cycle_graph():
    """a -> b -> a  (cycle), plus d isolated"""
    return {"a": ["b"], "b": ["a"], "d": []}


# ---------------------------------------------------------------------------
# annotate_nodes
# ---------------------------------------------------------------------------

def test_all_nodes_present_in_annotations(linear_graph):
    ann = annotate_nodes(linear_graph)
    assert set(ann.keys()) == {"a", "b", "c"}


def test_entry_point_labelled(linear_graph):
    ann = annotate_nodes(linear_graph)
    assert LABEL_ENTRY in ann["a"]


def test_leaf_labelled(linear_graph):
    ann = annotate_nodes(linear_graph)
    assert LABEL_LEAF in ann["c"]


def test_middle_node_has_no_special_label(linear_graph):
    ann = annotate_nodes(linear_graph)
    assert ann["b"] == []


def test_cycle_members_labelled(cycle_graph):
    ann = annotate_nodes(cycle_graph)
    assert LABEL_CYCLE in ann["a"]
    assert LABEL_CYCLE in ann["b"]


def test_isolated_node_labelled(cycle_graph):
    ann = annotate_nodes(cycle_graph)
    assert LABEL_ISOLATED in ann["d"]


def test_isolated_node_not_labelled_leaf(cycle_graph):
    ann = annotate_nodes(cycle_graph)
    assert LABEL_LEAF not in ann["d"]


def test_empty_graph_returns_empty():
    ann = annotate_nodes({})
    assert ann == {}


def test_single_node_no_edges():
    ann = annotate_nodes({"x": []})
    assert LABEL_ISOLATED in ann["x"]
    assert LABEL_ENTRY in ann["x"]


def test_entry_not_labelled_for_depended_on_node():
    # b is depended on by a, so b is NOT an entry point
    graph = {"a": ["b"], "b": []}
    ann = annotate_nodes(graph)
    assert LABEL_ENTRY not in ann["b"]


# ---------------------------------------------------------------------------
# filter_by_annotation
# ---------------------------------------------------------------------------

def test_filter_returns_correct_nodes(linear_graph):
    ann = annotate_nodes(linear_graph)
    entries = filter_by_annotation(ann, LABEL_ENTRY)
    assert entries == ["a"]


def test_filter_empty_when_no_match(linear_graph):
    ann = annotate_nodes(linear_graph)
    cycles = filter_by_annotation(ann, LABEL_CYCLE)
    assert cycles == []


def test_filter_returns_sorted_list(cycle_graph):
    ann = annotate_nodes(cycle_graph)
    members = filter_by_annotation(ann, LABEL_CYCLE)
    assert members == sorted(members)


def test_filter_isolated(cycle_graph):
    ann = annotate_nodes(cycle_graph)
    isolated = filter_by_annotation(ann, LABEL_ISOLATED)
    assert "d" in isolated
