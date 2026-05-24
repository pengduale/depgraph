"""Tests for depgraph.recommender."""

from __future__ import annotations

import pytest

from depgraph.recommender import (
    format_recommendations,
    get_recommendations,
    recommend_cycles,
    recommend_god_modules,
    recommend_high_coupling,
    recommend_isolated,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def clean_graph():
    return {
        "a": ["b"],
        "b": ["c"],
        "c": [],
    }


@pytest.fixture()
def cycle_graph():
    return {
        "a": ["b"],
        "b": ["a"],
        "c": [],
    }


@pytest.fixture()
def high_coupling_graph():
    return {
        "hub": ["a", "b", "c", "d", "e", "f"],
        "a": [], "b": [], "c": [], "d": [], "e": [], "f": [],
    }


@pytest.fixture()
def god_module_graph():
    return {
        "a": ["core"],
        "b": ["core"],
        "c": ["core"],
        "d": ["core"],
        "e": ["core"],
        "f": ["core"],
        "core": [],
    }


@pytest.fixture()
def isolated_graph():
    return {
        "a": ["b"],
        "b": [],
        "lone": [],
    }


# ---------------------------------------------------------------------------
# recommend_cycles
# ---------------------------------------------------------------------------

def test_recommend_cycles_clean(clean_graph):
    assert recommend_cycles(clean_graph) == []


def test_recommend_cycles_detects_cycle(cycle_graph):
    recs = recommend_cycles(cycle_graph)
    nodes = {r.node for r in recs}
    assert "a" in nodes or "b" in nodes


def test_recommend_cycles_severity(cycle_graph):
    recs = recommend_cycles(cycle_graph)
    assert all(r.severity == "error" for r in recs)


def test_recommend_cycles_category(cycle_graph):
    recs = recommend_cycles(cycle_graph)
    assert all(r.category == "cycle" for r in recs)


# ---------------------------------------------------------------------------
# recommend_high_coupling
# ---------------------------------------------------------------------------

def test_recommend_high_coupling_below_threshold(clean_graph):
    assert recommend_high_coupling(clean_graph, threshold=5) == []


def test_recommend_high_coupling_detects(high_coupling_graph):
    recs = recommend_high_coupling(high_coupling_graph, threshold=5)
    assert any(r.node == "hub" for r in recs)


def test_recommend_high_coupling_severity(high_coupling_graph):
    recs = recommend_high_coupling(high_coupling_graph, threshold=5)
    assert all(r.severity == "warning" for r in recs)


# ---------------------------------------------------------------------------
# recommend_god_modules
# ---------------------------------------------------------------------------

def test_recommend_god_modules_clean(clean_graph):
    assert recommend_god_modules(clean_graph, threshold=5) == []


def test_recommend_god_modules_detects(god_module_graph):
    recs = recommend_god_modules(god_module_graph, threshold=5)
    assert any(r.node == "core" for r in recs)


def test_recommend_god_modules_category(god_module_graph):
    recs = recommend_god_modules(god_module_graph, threshold=5)
    assert all(r.category == "god_module" for r in recs)


# ---------------------------------------------------------------------------
# recommend_isolated
# ---------------------------------------------------------------------------

def test_recommend_isolated_detects_lone(isolated_graph):
    recs = recommend_isolated(isolated_graph)
    assert any(r.node == "lone" for r in recs)


def test_recommend_isolated_does_not_flag_connected(isolated_graph):
    recs = recommend_isolated(isolated_graph)
    nodes = {r.node for r in recs}
    assert "a" not in nodes
    assert "b" not in nodes


def test_recommend_isolated_severity(isolated_graph):
    recs = recommend_isolated(isolated_graph)
    assert all(r.severity == "info" for r in recs)


# ---------------------------------------------------------------------------
# get_recommendations
# ---------------------------------------------------------------------------

def test_get_recommendations_empty_graph():
    recs = get_recommendations({})
    assert recs == []


def test_get_recommendations_combined(cycle_graph):
    recs = get_recommendations(cycle_graph)
    categories = {r.category for r in recs}
    assert "cycle" in categories


# ---------------------------------------------------------------------------
# format_recommendations
# ---------------------------------------------------------------------------

def test_format_recommendations_empty():
    result = format_recommendations([])
    assert "healthy" in result


def test_format_recommendations_contains_severity(cycle_graph):
    recs = get_recommendations(cycle_graph)
    text = format_recommendations(recs)
    assert "ERROR" in text


def test_format_recommendations_contains_node(isolated_graph):
    recs = recommend_isolated(isolated_graph)
    text = format_recommendations(recs)
    assert "lone" in text
