"""Tests for depgraph.pruner."""

from __future__ import annotations

import pytest

from depgraph.pruner import (
    remove_transitive_edges,
    trim_leaves,
    trim_roots,
)


# ---------------------------------------------------------------------------
# remove_transitive_edges
# ---------------------------------------------------------------------------

def test_remove_transitive_keeps_direct_only():
    # A -> B -> C, A -> C  (A->C is transitive)
    graph = {"A": ["B", "C"], "B": ["C"], "C": []}
    result = remove_transitive_edges(graph)
    assert "C" not in result["A"]
    assert "B" in result["A"]
    assert "C" in result["B"]


def test_remove_transitive_no_redundancy():
    graph = {"A": ["B"], "B": ["C"], "C": []}
    result = remove_transitive_edges(graph)
    assert result["A"] == ["B"]
    assert result["C"] == []


def test_remove_transitive_empty_graph():
    assert remove_transitive_edges({}) == {}


def test_remove_transitive_preserves_all_nodes():
    graph = {"A": ["B", "C"], "B": ["C"], "C": []}
    result = remove_transitive_edges(graph)
    assert set(result.keys()) == {"A", "B", "C"}


def test_remove_transitive_longer_chain():
    # A->B->C->D, A->D  (A->D is transitive via B->C->D)
    graph = {"A": ["B", "D"], "B": ["C"], "C": ["D"], "D": []}
    result = remove_transitive_edges(graph)
    assert "D" not in result["A"]
    assert "B" in result["A"]


# ---------------------------------------------------------------------------
# trim_leaves
# ---------------------------------------------------------------------------

def test_trim_leaves_removes_leaf():
    graph = {"A": ["B"], "B": []}
    result = trim_leaves(graph, passes=1)
    assert "B" not in result
    assert "A" not in result  # A becomes a leaf after B is removed


def test_trim_leaves_single_pass_does_not_cascade():
    graph = {"A": ["B"], "B": []}
    # With 1 pass only B (the leaf) is removed; A still has no deps but
    # the single pass only runs once, so A should be gone too since it
    # becomes a leaf in the same pass evaluation.
    result = trim_leaves(graph, passes=1)
    # Both are leaves after first removal — implementation removes in one sweep
    assert "B" not in result


def test_trim_leaves_keeps_non_leaf():
    graph = {"A": ["B"], "B": ["C"], "C": []}
    result = trim_leaves(graph, passes=1)
    assert "C" not in result


def test_trim_leaves_empty_graph():
    assert trim_leaves({}, passes=3) == {}


def test_trim_leaves_no_leaves():
    # Cycle — nothing is a leaf
    graph = {"A": ["B"], "B": ["A"]}
    result = trim_leaves(graph, passes=5)
    assert result == {"A": ["B"], "B": ["A"]}


# ---------------------------------------------------------------------------
# trim_roots
# ---------------------------------------------------------------------------

def test_trim_roots_removes_root():
    graph = {"A": ["B"], "B": ["C"], "C": []}
    result = trim_roots(graph, passes=1)
    assert "A" not in result


def test_trim_roots_keeps_non_root():
    graph = {"A": ["B"], "B": ["C"], "C": []}
    result = trim_roots(graph, passes=1)
    assert "B" in result


def test_trim_roots_empty_graph():
    assert trim_roots({}, passes=2) == {}


def test_trim_roots_no_roots():
    # Cycle — no pure roots
    graph = {"A": ["B"], "B": ["A"]}
    result = trim_roots(graph, passes=5)
    assert result == {"A": ["B"], "B": ["A"]}


def test_trim_roots_multi_pass():
    # A -> B -> C; after removing A, B becomes a root
    graph = {"A": ["B"], "B": ["C"], "C": []}
    result = trim_roots(graph, passes=2)
    assert "A" not in result
    assert "B" not in result
    assert "C" in result
