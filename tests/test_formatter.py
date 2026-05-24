"""Tests for depgraph.formatter."""

from __future__ import annotations

import pytest

from depgraph.formatter import (
    format_adjacency_list,
    format_edge_list,
    format_graph,
    format_table,
)


@pytest.fixture()
def simple_graph():
    return {
        "a": ["b", "c"],
        "b": ["c"],
        "c": [],
    }


# --- format_adjacency_list ---

def test_adjacency_list_contains_all_nodes(simple_graph):
    result = format_adjacency_list(simple_graph)
    assert "a ->" in result
    assert "b ->" in result
    assert "c ->" in result


def test_adjacency_list_none_for_no_deps(simple_graph):
    result = format_adjacency_list(simple_graph)
    assert "(none)" in result


def test_adjacency_list_empty_graph():
    result = format_adjacency_list({})
    assert "empty" in result.lower()


def test_adjacency_list_sorted_output(simple_graph):
    result = format_adjacency_list(simple_graph)
    lines = [l for l in result.splitlines() if "->" in l]
    nodes = [l.strip().split(" ")[0] for l in lines]
    assert nodes == sorted(nodes)


# --- format_edge_list ---

def test_edge_list_has_all_edges(simple_graph):
    result = format_edge_list(simple_graph)
    assert "a -> b" in result
    assert "a -> c" in result
    assert "b -> c" in result


def test_edge_list_no_edges():
    result = format_edge_list({"x": [], "y": []})
    assert "no edges" in result.lower()


def test_edge_list_empty_graph():
    result = format_edge_list({})
    assert "no edges" in result.lower()


# --- format_table ---

def test_table_has_header(simple_graph):
    result = format_table(simple_graph)
    assert "Source" in result
    assert "Target" in result


def test_table_has_separator(simple_graph):
    result = format_table(simple_graph)
    assert "---" in result


def test_table_no_edges():
    result = format_table({"x": []})
    assert "No edges" in result


# --- format_graph dispatcher ---

def test_format_graph_adjacency(simple_graph):
    result = format_graph(simple_graph, style="adjacency")
    assert "Adjacency list" in result


def test_format_graph_edges(simple_graph):
    result = format_graph(simple_graph, style="edges")
    assert "Edge list" in result


def test_format_graph_table(simple_graph):
    result = format_graph(simple_graph, style="table")
    assert "Source" in result


def test_format_graph_invalid_style(simple_graph):
    with pytest.raises(ValueError, match="Unknown format style"):
        format_graph(simple_graph, style="xml")
