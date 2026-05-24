"""Tests for depgraph.inspector."""
import pytest

from depgraph.inspector import (
    find_bottlenecks,
    format_node_report,
    inspect_all_nodes,
    inspect_edge,
    inspect_node,
)


@pytest.fixture
def graph():
    return {
        "pkg.a": ["pkg.b", "pkg.c"],
        "pkg.b": ["pkg.c"],
        "pkg.c": [],
        "pkg.d": [],
    }


def test_inspect_node_out_degree(graph):
    info = inspect_node(graph, "pkg.a")
    assert info["out_degree"] == 2


def test_inspect_node_in_degree(graph):
    info = inspect_node(graph, "pkg.c")
    assert info["in_degree"] == 2


def test_inspect_node_dependencies_sorted(graph):
    info = inspect_node(graph, "pkg.a")
    assert info["dependencies"] == ["pkg.b", "pkg.c"]


def test_inspect_node_dependents_sorted(graph):
    info = inspect_node(graph, "pkg.c")
    assert info["dependents"] == ["pkg.a", "pkg.b"]


def test_inspect_node_is_root(graph):
    assert inspect_node(graph, "pkg.a")["is_root"] is True
    assert inspect_node(graph, "pkg.c")["is_root"] is False


def test_inspect_node_is_leaf(graph):
    assert inspect_node(graph, "pkg.c")["is_leaf"] is True
    assert inspect_node(graph, "pkg.a")["is_leaf"] is False


def test_inspect_node_is_isolated(graph):
    assert inspect_node(graph, "pkg.d")["is_isolated"] is True
    assert inspect_node(graph, "pkg.a")["is_isolated"] is False


def test_inspect_node_missing(graph):
    info = inspect_node(graph, "pkg.x")
    assert "error" in info


def test_inspect_edge_exists(graph):
    info = inspect_edge(graph, "pkg.a", "pkg.b")
    assert info["exists"] is True


def test_inspect_edge_not_exists(graph):
    info = inspect_edge(graph, "pkg.b", "pkg.a")
    assert info["exists"] is False


def test_inspect_edge_missing_src(graph):
    info = inspect_edge(graph, "pkg.z", "pkg.a")
    assert info["exists"] is False
    assert info["src_exists"] is False


def test_inspect_all_nodes_count(graph):
    result = inspect_all_nodes(graph)
    assert len(result) == 4


def test_inspect_all_nodes_sorted(graph):
    result = inspect_all_nodes(graph)
    names = [r["node"] for r in result]
    assert names == sorted(names)


def test_find_bottlenecks_threshold_two(graph):
    result = find_bottlenecks(graph, threshold=2)
    assert result == ["pkg.c"]


def test_find_bottlenecks_threshold_one(graph):
    result = find_bottlenecks(graph, threshold=1)
    assert "pkg.b" in result
    assert "pkg.c" in result


def test_find_bottlenecks_none(graph):
    result = find_bottlenecks(graph, threshold=10)
    assert result == []


def test_format_node_report_contains_node_name(graph):
    info = inspect_node(graph, "pkg.a")
    report = format_node_report(info)
    assert "pkg.a" in report


def test_format_node_report_error(graph):
    info = inspect_node(graph, "missing")
    report = format_node_report(info)
    assert "missing" in report
