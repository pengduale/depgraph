"""Tests for depgraph.renamer."""

from __future__ import annotations

import pytest

from depgraph.renamer import (
    rename_node,
    rename_nodes,
    normalize_names,
    format_rename_diff,
)


@pytest.fixture()
def simple_graph():
    return {
        "app.main": ["app.utils", "app.models"],
        "app.utils": ["app.models"],
        "app.models": [],
    }


def test_rename_node_updates_key(simple_graph):
    result = rename_node(simple_graph, "app.utils", "app.helpers")
    assert "app.helpers" in result
    assert "app.utils" not in result


def test_rename_node_updates_deps(simple_graph):
    result = rename_node(simple_graph, "app.utils", "app.helpers")
    assert "app.helpers" in result["app.main"]
    assert "app.utils" not in result["app.main"]


def test_rename_node_unknown_returns_copy(simple_graph):
    result = rename_node(simple_graph, "nonexistent", "new_name")
    assert result == simple_graph
    assert result is not simple_graph


def test_rename_node_conflict_raises(simple_graph):
    with pytest.raises(ValueError, match="already exists"):
        rename_node(simple_graph, "app.utils", "app.models")


def test_rename_node_same_name_is_noop(simple_graph):
    result = rename_node(simple_graph, "app.utils", "app.utils")
    assert result == simple_graph


def test_rename_nodes_multiple(simple_graph):
    mapping = {"app.main": "core.main", "app.models": "core.models"}
    result = rename_nodes(simple_graph, mapping)
    assert "core.main" in result
    assert "core.models" in result
    assert "app.main" not in result
    assert "app.models" not in result


def test_rename_nodes_empty_mapping(simple_graph):
    result = rename_nodes(simple_graph, {})
    assert result == simple_graph


def test_normalize_names_lowercases(simple_graph):
    upper_graph = {
        "App.Main": ["App.Utils"],
        "App.Utils": [],
    }
    result = normalize_names(upper_graph)
    assert "app.main" in result
    assert "app.utils" in result
    assert "app.utils" in result["app.main"]


def test_normalize_names_collision_raises():
    graph = {"App": ["Base"], "app": ["Base"], "Base": []}
    with pytest.raises(ValueError, match="collision"):
        normalize_names(graph)


def test_normalize_custom_transform():
    graph = {"mod_a": ["mod_b"], "mod_b": []}
    result = normalize_names(graph, transform=lambda s: s.replace("_", "."))
    assert "mod.a" in result
    assert "mod.b" in result


def test_format_rename_diff_detects_changes(simple_graph):
    new_graph = rename_node(simple_graph, "app.utils", "app.helpers")
    diff = format_rename_diff(simple_graph, new_graph)
    assert "app.utils" in diff
    assert "app.helpers" in diff


def test_format_rename_diff_no_changes(simple_graph):
    diff = format_rename_diff(simple_graph, simple_graph)
    assert "No node renames" in diff
