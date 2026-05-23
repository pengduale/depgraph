"""Tests for depgraph.highlighter module."""

import pytest
from depgraph.highlighter import (
    highlight_node,
    get_highlighted_edges,
    _find_ancestors,
    _find_descendants,
)


SAMPLE_GRAPH = {
    "a": ["b", "c"],
    "b": ["d"],
    "c": ["d"],
    "d": [],
    "e": [],  # isolated
}


def test_highlight_node_focus_class():
    result = highlight_node(SAMPLE_GRAPH, "b")
    assert result["b"] == "focus"


def test_highlight_node_ancestor():
    result = highlight_node(SAMPLE_GRAPH, "b")
    assert result["a"] == "ancestor"


def test_highlight_node_descendant():
    result = highlight_node(SAMPLE_GRAPH, "b")
    assert result["d"] == "descendant"


def test_highlight_node_default_for_unrelated():
    result = highlight_node(SAMPLE_GRAPH, "b")
    assert result["c"] == "default"
    assert result["e"] == "default"


def test_highlight_node_no_ancestors():
    result = highlight_node(SAMPLE_GRAPH, "b", include_ancestors=False)
    assert result["a"] == "default"
    assert result["d"] == "descendant"


def test_highlight_node_no_descendants():
    result = highlight_node(SAMPLE_GRAPH, "b", include_descendants=False)
    assert result["d"] == "default"
    assert result["a"] == "ancestor"


def test_highlight_node_invalid_node():
    with pytest.raises(ValueError, match="not found in graph"):
        highlight_node(SAMPLE_GRAPH, "nonexistent")


def test_find_ancestors_direct():
    ancestors = _find_ancestors(SAMPLE_GRAPH, "d")
    assert "b" in ancestors
    assert "c" in ancestors


def test_find_ancestors_transitive():
    ancestors = _find_ancestors(SAMPLE_GRAPH, "d")
    assert "a" in ancestors


def test_find_ancestors_root_has_none():
    ancestors = _find_ancestors(SAMPLE_GRAPH, "a")
    assert len(ancestors) == 0


def test_find_descendants_direct():
    descendants = _find_descendants(SAMPLE_GRAPH, "a")
    assert "b" in descendants
    assert "c" in descendants


def test_find_descendants_transitive():
    descendants = _find_descendants(SAMPLE_GRAPH, "a")
    assert "d" in descendants


def test_find_descendants_leaf_has_none():
    descendants = _find_descendants(SAMPLE_GRAPH, "d")
    assert len(descendants) == 0


def test_get_highlighted_edges_focus_edge():
    highlights = highlight_node(SAMPLE_GRAPH, "b")
    edges = get_highlighted_edges(SAMPLE_GRAPH, highlights)
    assert edges[("a", "b")] == "edge-focus"
    assert edges[("b", "d")] == "edge-focus"


def test_get_highlighted_edges_default_edge():
    highlights = highlight_node(SAMPLE_GRAPH, "b")
    edges = get_highlighted_edges(SAMPLE_GRAPH, highlights)
    assert edges[("a", "c")] == "edge-default"
