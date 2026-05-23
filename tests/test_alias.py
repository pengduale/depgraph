"""Tests for depgraph.alias and depgraph.alias_cmd."""

from __future__ import annotations

import json
import pytest

from depgraph.alias import (
    build_alias_map,
    resolve_node,
    apply_aliases,
    reverse_alias_map,
    aliases_for_prefix,
)


# ---------------------------------------------------------------------------
# build_alias_map
# ---------------------------------------------------------------------------

def test_build_alias_map_basic():
    am = build_alias_map([("core", "myproject.core"), ("util", "myproject.util")])
    assert am == {"core": "myproject.core", "util": "myproject.util"}


def test_build_alias_map_empty():
    assert build_alias_map([]) == {}


def test_build_alias_map_duplicate_raises():
    with pytest.raises(ValueError, match="Duplicate alias"):
        build_alias_map([("core", "myproject.core"), ("core", "other.core")])


# ---------------------------------------------------------------------------
# resolve_node
# ---------------------------------------------------------------------------

def test_resolve_node_known_alias():
    am = {"core": "myproject.core"}
    assert resolve_node("core", am) == "myproject.core"


def test_resolve_node_unknown_returns_original():
    am = {"core": "myproject.core"}
    assert resolve_node("other", am) == "other"


# ---------------------------------------------------------------------------
# apply_aliases
# ---------------------------------------------------------------------------

def test_apply_aliases_resolves_keys_and_values():
    graph = {"core": ["util"], "util": []}
    am = {"core": "myproject.core", "util": "myproject.util"}
    result = apply_aliases(graph, am)
    assert "myproject.core" in result
    assert result["myproject.core"] == ["myproject.util"]
    assert result["myproject.util"] == []


def test_apply_aliases_merges_collapsed_keys():
    # Two aliases that resolve to the same full path should be merged.
    graph = {"a": ["x"], "b": ["y"]}
    am = {"a": "pkg", "b": "pkg"}  # both collapse to 'pkg'
    result = apply_aliases(graph, am)
    assert set(result["pkg"]) == {"x", "y"}


def test_apply_aliases_no_aliases_unchanged():
    graph = {"foo": ["bar"], "bar": []}
    result = apply_aliases(graph, {})
    assert result == graph


# ---------------------------------------------------------------------------
# reverse_alias_map
# ---------------------------------------------------------------------------

def test_reverse_alias_map():
    am = {"core": "myproject.core", "util": "myproject.util"}
    rev = reverse_alias_map(am)
    assert rev["myproject.core"] == "core"
    assert rev["myproject.util"] == "util"


def test_reverse_alias_map_first_alias_wins():
    am = {"a": "pkg", "b": "pkg"}
    rev = reverse_alias_map(am)
    assert rev["pkg"] == "a"  # first encountered


# ---------------------------------------------------------------------------
# aliases_for_prefix
# ---------------------------------------------------------------------------

def test_aliases_for_prefix_filters_correctly():
    am = {"core": "myproject.core", "util": "myproject.util", "ext": "external.lib"}
    subset = aliases_for_prefix("myproject", am)
    assert set(subset.keys()) == {"core", "util"}


def test_aliases_for_prefix_no_match():
    am = {"core": "myproject.core"}
    assert aliases_for_prefix("other", am) == {}


# ---------------------------------------------------------------------------
# alias_cmd integration
# ---------------------------------------------------------------------------

def test_alias_cmd_parse_defaults():
    from depgraph.alias_cmd import parse_alias_args
    args = parse_alias_args(["mydir"])
    assert args.path == "mydir"
    assert args.aliases == []
    assert args.format == "text"


def test_alias_cmd_parse_custom():
    from depgraph.alias_cmd import parse_alias_args
    args = parse_alias_args(["mydir", "--alias", "core=pkg.core", "--format", "json"])
    assert args.aliases == ["core=pkg.core"]
    assert args.format == "json"
