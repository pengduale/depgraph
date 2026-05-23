"""Tests for depgraph.cluster."""

from __future__ import annotations

import pytest
from depgraph.cluster import (
    cluster_by_prefix,
    merge_small_clusters,
    intra_cluster_edges,
    cluster_summary,
)


# ---------------------------------------------------------------------------
# cluster_by_prefix
# ---------------------------------------------------------------------------

def test_cluster_by_prefix_depth_one():
    nodes = ["app.models", "app.views", "lib.utils"]
    result = cluster_by_prefix(nodes, depth=1)
    assert set(result["app"]) == {"app.models", "app.views"}
    assert result["lib"] == ["lib.utils"]


def test_cluster_by_prefix_depth_two():
    nodes = ["a.b.c", "a.b.d", "a.x.y"]
    result = cluster_by_prefix(nodes, depth=2)
    assert set(result["a.b"]) == {"a.b.c", "a.b.d"}
    assert result["a.x"] == ["a.x.y"]


def test_cluster_by_prefix_no_dot():
    nodes = ["alpha", "beta", "gamma"]
    result = cluster_by_prefix(nodes, depth=1)
    assert "alpha" in result
    assert "beta" in result


def test_cluster_by_prefix_empty():
    assert cluster_by_prefix([], depth=1) == {}


def test_cluster_by_prefix_depth_exceeds_parts():
    nodes = ["short"]
    result = cluster_by_prefix(nodes, depth=5)
    assert result == {"short": ["short"]}


# ---------------------------------------------------------------------------
# merge_small_clusters
# ---------------------------------------------------------------------------

def test_merge_small_clusters_moves_singletons():
    clusters = {"a": ["a.x"], "b": ["b.x", "b.y"]}
    result = merge_small_clusters(clusters, min_size=2)
    assert "a" not in result
    assert set(result["other"]) == {"a.x"}
    assert "b" in result


def test_merge_small_clusters_all_large():
    clusters = {"a": ["a.x", "a.y"], "b": ["b.x", "b.y"]}
    result = merge_small_clusters(clusters, min_size=2)
    assert "other" not in result
    assert "a" in result and "b" in result


def test_merge_small_clusters_all_small():
    clusters = {"a": ["a.x"], "b": ["b.x"]}
    result = merge_small_clusters(clusters, min_size=3)
    assert list(result.keys()) == ["other"]
    assert set(result["other"]) == {"a.x", "b.x"}


# ---------------------------------------------------------------------------
# intra_cluster_edges
# ---------------------------------------------------------------------------

def test_intra_cluster_edges_same_cluster():
    graph = {"app.models": ["app.utils"], "app.utils": []}
    clusters = {"app": ["app.models", "app.utils"]}
    result = intra_cluster_edges(graph, clusters)
    assert ("app.models", "app.utils") in result["app"]


def test_intra_cluster_edges_cross_cluster_excluded():
    graph = {"app.views": ["lib.helpers"], "lib.helpers": []}
    clusters = {"app": ["app.views"], "lib": ["lib.helpers"]}
    result = intra_cluster_edges(graph, clusters)
    assert result["app"] == []
    assert result["lib"] == []


def test_intra_cluster_edges_empty_graph():
    result = intra_cluster_edges({}, {"app": ["app.x"]})
    assert result["app"] == []


# ---------------------------------------------------------------------------
# cluster_summary
# ---------------------------------------------------------------------------

def test_cluster_summary_sorted_by_size_desc():
    clusters = {"small": ["s.x"], "big": ["b.x", "b.y", "b.z"]}
    summary = cluster_summary(clusters)
    assert summary[0]["cluster"] == "big"
    assert summary[1]["cluster"] == "small"


def test_cluster_summary_members_sorted():
    clusters = {"app": ["app.z", "app.a", "app.m"]}
    summary = cluster_summary(clusters)
    assert summary[0]["members"] == ["app.a", "app.m", "app.z"]
