"""Tests for depgraph.search module."""

import pytest
from depgraph.search import (
    find_nodes_by_name,
    find_paths,
    find_dependents,
    find_dependencies,
)


@pytest.fixture
def sample_graph():
    return {
        "app.main": ["app.utils", "app.models"],
        "app.utils": ["lib.helpers"],
        "app.models": ["lib.helpers", "lib.db"],
        "lib.helpers": [],
        "lib.db": [],
        "standalone": [],
    }


# --- find_nodes_by_name ---

def test_find_nodes_by_name_basic(sample_graph):
    result = find_nodes_by_name(sample_graph, "app")
    assert result == ["app.main", "app.models", "app.utils"]


def test_find_nodes_by_name_case_insensitive(sample_graph):
    result = find_nodes_by_name(sample_graph, "LIB")
    assert "lib.helpers" in result
    assert "lib.db" in result


def test_find_nodes_by_name_case_sensitive(sample_graph):
    result = find_nodes_by_name(sample_graph, "LIB", case_sensitive=True)
    assert result == []


def test_find_nodes_by_name_no_match(sample_graph):
    assert find_nodes_by_name(sample_graph, "zzz") == []


def test_find_nodes_by_name_exact(sample_graph):
    result = find_nodes_by_name(sample_graph, "standalone")
    assert result == ["standalone"]


# --- find_paths ---

def test_find_paths_direct(sample_graph):
    paths = find_paths(sample_graph, "app.main", "app.utils")
    assert ["app.main", "app.utils"] in paths


def test_find_paths_indirect(sample_graph):
    paths = find_paths(sample_graph, "app.main", "lib.db")
    assert ["app.main", "app.models", "lib.db"] in paths


def test_find_paths_no_path(sample_graph):
    paths = find_paths(sample_graph, "lib.db", "app.main")
    assert paths == []


def test_find_paths_unknown_source(sample_graph):
    assert find_paths(sample_graph, "unknown", "app.main") == []


def test_find_paths_same_node(sample_graph):
    paths = find_paths(sample_graph, "app.utils", "app.utils")
    assert ["app.utils"] in paths


# --- find_dependents ---

def test_find_dependents_direct(sample_graph):
    result = find_dependents(sample_graph, "lib.helpers")
    assert "app.utils" in result
    assert "app.models" in result


def test_find_dependents_transitive(sample_graph):
    result = find_dependents(sample_graph, "lib.helpers")
    assert "app.main" in result


def test_find_dependents_no_dependents(sample_graph):
    assert find_dependents(sample_graph, "app.main") == []


# --- find_dependencies ---

def test_find_dependencies_direct(sample_graph):
    result = find_dependencies(sample_graph, "app.utils")
    assert result == ["lib.helpers"]


def test_find_dependencies_transitive(sample_graph):
    result = find_dependencies(sample_graph, "app.main")
    assert "lib.helpers" in result
    assert "lib.db" in result


def test_find_dependencies_leaf(sample_graph):
    assert find_dependencies(sample_graph, "lib.db") == []


def test_find_dependencies_unknown_node(sample_graph):
    assert find_dependencies(sample_graph, "ghost") == []
