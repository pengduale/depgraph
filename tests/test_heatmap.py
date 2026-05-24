"""Tests for depgraph.heatmap."""

from __future__ import annotations

import pytest

from depgraph.heatmap import (
    build_heatmap,
    compute_heat,
    format_heatmap,
    heat_to_color,
)


@pytest.fixture()
def simple_graph():
    return {
        "a": ["b", "c"],
        "b": ["c"],
        "c": [],
    }


# --- compute_heat ---

def test_compute_heat_all_nodes_present(simple_graph):
    heat = compute_heat(simple_graph)
    assert set(heat.keys()) == {"a", "b", "c"}


def test_compute_heat_in_degree_max_is_one(simple_graph):
    heat = compute_heat(simple_graph, metric="in_degree")
    assert max(heat.values()) == pytest.approx(1.0)


def test_compute_heat_in_degree_root_is_zero(simple_graph):
    heat = compute_heat(simple_graph, metric="in_degree")
    assert heat["a"] == pytest.approx(0.0)


def test_compute_heat_out_degree_leaf_is_zero(simple_graph):
    heat = compute_heat(simple_graph, metric="out_degree")
    assert heat["c"] == pytest.approx(0.0)


def test_compute_heat_out_degree_root_is_one(simple_graph):
    heat = compute_heat(simple_graph, metric="out_degree")
    assert heat["a"] == pytest.approx(1.0)


def test_compute_heat_total_degree(simple_graph):
    heat = compute_heat(simple_graph, metric="total_degree")
    assert max(heat.values()) == pytest.approx(1.0)


def test_compute_heat_empty_graph():
    assert compute_heat({}) == {}


def test_compute_heat_unknown_metric_raises(simple_graph):
    with pytest.raises(ValueError, match="Unknown metric"):
        compute_heat(simple_graph, metric="bogus")


def test_compute_heat_uniform_graph():
    g = {"x": ["y"], "y": ["x"]}  # each node has in_degree 1
    heat = compute_heat(g, metric="in_degree")
    assert heat["x"] == pytest.approx(heat["y"])


# --- heat_to_color ---

def test_heat_to_color_red_zero():
    color = heat_to_color(0.0, palette="red")
    assert color.startswith("#")
    assert len(color) == 7


def test_heat_to_color_red_one():
    color = heat_to_color(1.0, palette="red")
    assert color == "#ff2828"  # intensity=255, low=220-180=40 -> 0x28


def test_heat_to_color_blue_palette():
    color = heat_to_color(1.0, palette="blue")
    assert color.endswith("ff")


def test_heat_to_color_green_palette():
    color = heat_to_color(1.0, palette="green")
    assert color[3:5] == "ff"


def test_heat_to_color_clamps_above_one():
    c1 = heat_to_color(1.0)
    c2 = heat_to_color(2.0)
    assert c1 == c2


def test_heat_to_color_unknown_palette_raises():
    with pytest.raises(ValueError, match="Unknown palette"):
        heat_to_color(0.5, palette="purple")


# --- build_heatmap ---

def test_build_heatmap_returns_hex_colors(simple_graph):
    colors = build_heatmap(simple_graph)
    for color in colors.values():
        assert color.startswith("#")
        assert len(color) == 7


def test_build_heatmap_all_nodes_present(simple_graph):
    colors = build_heatmap(simple_graph)
    assert set(colors.keys()) == set(simple_graph.keys())


# --- format_heatmap ---

def test_format_heatmap_contains_node_names(simple_graph):
    heat = compute_heat(simple_graph)
    text = format_heatmap(heat)
    for node in simple_graph:
        assert node in text


def test_format_heatmap_empty():
    assert format_heatmap({}) == "(empty graph)"


def test_format_heatmap_sorted_descending(simple_graph):
    heat = compute_heat(simple_graph, metric="in_degree")
    text = format_heatmap(heat)
    lines = [l for l in text.splitlines() if l and not l.startswith("-") and l != "Node" + " " * 36 + "Heat"]
    values = [float(l.split()[-1]) for l in lines if l.strip()]
    assert values == sorted(values, reverse=True)
