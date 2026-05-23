"""Tests for depgraph.layout module."""

import math
import pytest
from depgraph.layout import layout_hierarchical, layout_circular, get_layout


SIMPLE_GRAPH = {
    "a": ["b", "c"],
    "b": ["d"],
    "c": ["d"],
    "d": [],
}


def test_hierarchical_all_nodes_present():
    pos = layout_hierarchical(SIMPLE_GRAPH)
    assert set(pos.keys()) == {"a", "b", "c", "d"}


def test_hierarchical_root_at_top():
    pos = layout_hierarchical(SIMPLE_GRAPH)
    # 'a' has no incoming edges — should be in layer 0 (y=0)
    assert pos["a"][1] == 0.0


def test_hierarchical_leaf_below_root():
    pos = layout_hierarchical(SIMPLE_GRAPH)
    # 'd' is a leaf — its y should be greater than 'a'
    assert pos["d"][1] > pos["a"][1]


def test_hierarchical_empty_graph():
    pos = layout_hierarchical({})
    assert pos == {}


def test_hierarchical_single_node():
    pos = layout_hierarchical({"x": []})
    assert "x" in pos
    assert pos["x"] == (0.0, 0.0)


def test_hierarchical_custom_spacing():
    pos = layout_hierarchical({"a": ["b"], "b": []}, spacing_x=100.0, spacing_y=50.0)
    # 'b' is one layer below 'a'
    assert pos["b"][1] - pos["a"][1] == pytest.approx(50.0)


def test_circular_all_nodes_present():
    pos = layout_circular(SIMPLE_GRAPH)
    assert set(pos.keys()) == {"a", "b", "c", "d"}


def test_circular_nodes_on_circle():
    radius = 200.0
    pos = layout_circular(SIMPLE_GRAPH, radius=radius)
    for node, (x, y) in pos.items():
        dist = math.sqrt(x ** 2 + y ** 2)
        assert dist == pytest.approx(radius, abs=0.1), f"{node} not on circle"


def test_circular_empty_graph():
    pos = layout_circular({})
    assert pos == {}


def test_circular_single_node():
    pos = layout_circular({"only": []})
    assert "only" in pos
    x, y = pos["only"]
    assert math.sqrt(x ** 2 + y ** 2) == pytest.approx(300.0, abs=0.1)


def test_get_layout_hierarchical():
    pos = get_layout("hierarchical", SIMPLE_GRAPH)
    assert set(pos.keys()) == {"a", "b", "c", "d"}


def test_get_layout_circular():
    pos = get_layout("circular", SIMPLE_GRAPH)
    assert set(pos.keys()) == {"a", "b", "c", "d"}


def test_get_layout_unknown_raises():
    with pytest.raises(ValueError, match="Unknown layout"):
        get_layout("unknown", SIMPLE_GRAPH)


def test_get_layout_passes_kwargs():
    pos = get_layout("hierarchical", {"a": ["b"], "b": []}, spacing_y=60.0)
    assert pos["b"][1] == pytest.approx(60.0)
