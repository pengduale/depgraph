"""Tests for depgraph.analyzer and depgraph.report."""

import pytest

from depgraph.analyzer import (
    compute_metrics,
    find_cycles,
    find_entry_points,
    find_most_depended_on,
)
from depgraph.report import generate_report


SIMPLE_GRAPH = {
    "a": ["b", "c"],
    "b": ["c"],
    "c": [],
}

CYCLIC_GRAPH = {
    "x": ["y"],
    "y": ["z"],
    "z": ["x"],
}


# --- find_cycles ---

def test_find_cycles_no_cycles():
    assert find_cycles(SIMPLE_GRAPH) == []


def test_find_cycles_detects_cycle():
    cycles = find_cycles(CYCLIC_GRAPH)
    assert len(cycles) >= 1
    # Each reported cycle should start and end at the same node
    for cycle in cycles:
        assert cycle[0] == cycle[-1]


def test_find_cycles_self_loop():
    graph = {"a": ["a"]}
    cycles = find_cycles(graph)
    assert any("a" in c for c in cycles)


# --- compute_metrics ---

def test_compute_metrics_out_degree():
    metrics = compute_metrics(SIMPLE_GRAPH)
    assert metrics["a"]["out_degree"] == 2
    assert metrics["b"]["out_degree"] == 1
    assert metrics["c"]["out_degree"] == 0


def test_compute_metrics_in_degree():
    metrics = compute_metrics(SIMPLE_GRAPH)
    assert metrics["c"]["in_degree"] == 2
    assert metrics["b"]["in_degree"] == 1
    assert metrics["a"]["in_degree"] == 0


# --- find_entry_points ---

def test_find_entry_points_simple():
    entries = find_entry_points(SIMPLE_GRAPH)
    assert entries == ["a"]


def test_find_entry_points_cyclic_graph_empty():
    # In a pure cycle every node has an in-edge
    entries = find_entry_points(CYCLIC_GRAPH)
    assert entries == []


# --- find_most_depended_on ---

def test_find_most_depended_on_top1():
    top = find_most_depended_on(SIMPLE_GRAPH, top_n=1)
    assert top[0][0] == "c"
    assert top[0][1] == 2


def test_find_most_depended_on_respects_top_n():
    top = find_most_depended_on(SIMPLE_GRAPH, top_n=2)
    assert len(top) == 2


# --- generate_report ---

def test_generate_report_contains_summary():
    report = generate_report(SIMPLE_GRAPH)
    assert "Modules" in report
    assert "Edges" in report


def test_generate_report_no_cycle_message():
    report = generate_report(SIMPLE_GRAPH)
    assert "No circular dependencies" in report


def test_generate_report_cycle_warning():
    report = generate_report(CYCLIC_GRAPH)
    assert "Circular dependencies" in report
