"""Tests for depgraph.summarizer."""

import pytest
from depgraph.summarizer import summarize, format_summary


@pytest.fixture
def simple_graph():
    return {
        "a": ["b", "c"],
        "b": ["c"],
        "c": [],
    }


@pytest.fixture
def cycle_graph():
    return {
        "x": ["y"],
        "y": ["z"],
        "z": ["x"],
    }


def test_summary_node_count(simple_graph):
    s = summarize(simple_graph)
    assert s["total_nodes"] == 3


def test_summary_edge_count(simple_graph):
    s = summarize(simple_graph)
    assert s["total_edges"] == 3


def test_summary_avg_out_degree(simple_graph):
    s = summarize(simple_graph)
    assert s["average_out_degree"] == pytest.approx(1.0)


def test_summary_entry_points(simple_graph):
    s = summarize(simple_graph)
    assert s["entry_points"] == ["a"]


def test_summary_no_cycles(simple_graph):
    s = summarize(simple_graph)
    assert s["cycles_detected"] is False
    assert s["cycle_count"] == 0
    assert s["cycles"] == []


def test_summary_detects_cycles(cycle_graph):
    s = summarize(cycle_graph)
    assert s["cycles_detected"] is True
    assert s["cycle_count"] >= 1


def test_summary_most_imported(simple_graph):
    s = summarize(simple_graph)
    assert s["most_imported_node"] == "c"
    assert s["most_imported_count"] == 2


def test_summary_empty_graph():
    s = summarize({})
    assert s["total_nodes"] == 0
    assert s["total_edges"] == 0
    assert s["average_out_degree"] == 0.0
    assert s["entry_points"] == []
    assert s["most_imported_node"] is None


def test_format_summary_contains_key_sections(simple_graph):
    s = summarize(simple_graph)
    text = format_summary(s)
    assert "Nodes" in text
    assert "Edges" in text
    assert "Entry points" in text
    assert "Cycles" in text


def test_format_summary_shows_no_cycles(simple_graph):
    s = summarize(simple_graph)
    text = format_summary(s)
    assert "no" in text


def test_format_summary_shows_yes_cycles(cycle_graph):
    s = summarize(cycle_graph)
    text = format_summary(s)
    assert "YES" in text
