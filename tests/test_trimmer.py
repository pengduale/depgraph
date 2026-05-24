"""Tests for depgraph.trimmer."""

import pytest
from depgraph.trimmer import (
    trim_by_in_degree,
    trim_by_out_degree,
    trim_by_total_degree,
    format_trimmed,
)


@pytest.fixture
def graph():
    # a -> b -> d
    # a -> c
    # d -> e
    return {
        "a": ["b", "c"],
        "b": ["d"],
        "c": [],
        "d": ["e"],
        "e": [],
    }


# --- trim_by_in_degree ---

def test_trim_in_degree_zero_keeps_all(graph):
    result = trim_by_in_degree(graph, 0)
    assert set(result) == set(graph)


def test_trim_in_degree_one_removes_root(graph):
    # 'a' has in-degree 0, so it should be removed when min_in=1
    result = trim_by_in_degree(graph, 1)
    assert "a" not in result


def test_trim_in_degree_removes_dangling_edges(graph):
    result = trim_by_in_degree(graph, 1)
    for deps in result.values():
        for dep in deps:
            assert dep in result


def test_trim_in_degree_high_threshold_returns_empty(graph):
    result = trim_by_in_degree(graph, 10)
    assert result == {}


# --- trim_by_out_degree ---

def test_trim_out_degree_zero_keeps_all(graph):
    result = trim_by_out_degree(graph, 0)
    assert set(result) == set(graph)


def test_trim_out_degree_one_removes_leaves(graph):
    # 'c' and 'e' have out-degree 0
    result = trim_by_out_degree(graph, 1)
    assert "c" not in result
    assert "e" not in result


def test_trim_out_degree_two_keeps_only_high_out(graph):
    # only 'a' has out-degree >= 2
    result = trim_by_out_degree(graph, 2)
    assert set(result) == {"a"}


def test_trim_out_degree_removes_dangling_edges(graph):
    result = trim_by_out_degree(graph, 1)
    for deps in result.values():
        for dep in deps:
            assert dep in result


# --- trim_by_total_degree ---

def test_trim_total_degree_zero_keeps_all(graph):
    result = trim_by_total_degree(graph, 0)
    assert set(result) == set(graph)


def test_trim_total_degree_removes_isolated_style_nodes(graph):
    # 'e' has in=1, out=0 => total=1; removed when min_total=2
    result = trim_by_total_degree(graph, 2)
    assert "e" not in result


def test_trim_total_degree_empty_graph():
    result = trim_by_total_degree({}, 1)
    assert result == {}


# --- format_trimmed ---

def test_format_trimmed_shows_removed_count(graph):
    trimmed = trim_by_in_degree(graph, 1)
    output = format_trimmed(graph, trimmed)
    assert "removed" in output


def test_format_trimmed_no_change():
    g = {"a": ["b"], "b": []}
    output = format_trimmed(g, g)
    assert "removed 0" in output


def test_format_trimmed_lists_removed_nodes(graph):
    trimmed = trim_by_out_degree(graph, 1)
    output = format_trimmed(graph, trimmed)
    assert "Removed nodes" in output
