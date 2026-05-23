"""Module alias management: define short aliases for long module paths."""

from __future__ import annotations

from typing import Dict, Optional


AliasMap = Dict[str, str]  # alias -> full module path


def build_alias_map(pairs: list[tuple[str, str]]) -> AliasMap:
    """Build an alias map from a list of (alias, full_path) pairs.

    Raises ValueError on duplicate aliases.
    """
    alias_map: AliasMap = {}
    for alias, full_path in pairs:
        if alias in alias_map:
            raise ValueError(
                f"Duplicate alias '{alias}': already mapped to '{alias_map[alias]}'"
            )
        alias_map[alias] = full_path
    return alias_map


def resolve_node(name: str, alias_map: AliasMap) -> str:
    """Return the full module path for *name*, or *name* itself if no alias exists."""
    return alias_map.get(name, name)


def apply_aliases(
    graph: dict[str, list[str]],
    alias_map: AliasMap,
) -> dict[str, list[str]]:
    """Return a new graph with all node names resolved through *alias_map*.

    Both keys (importers) and values (importees) are resolved.
    """
    resolved: dict[str, list[str]] = {}
    for node, deps in graph.items():
        new_node = resolve_node(node, alias_map)
        new_deps = [resolve_node(d, alias_map) for d in deps]
        # Merge in case two aliases collapse to the same key
        if new_node in resolved:
            existing = resolved[new_node]
            for dep in new_deps:
                if dep not in existing:
                    existing.append(dep)
        else:
            resolved[new_node] = new_deps
    return resolved


def reverse_alias_map(alias_map: AliasMap) -> dict[str, str]:
    """Return a mapping from full module path -> alias (first alias wins)."""
    reverse: dict[str, str] = {}
    for alias, full_path in alias_map.items():
        if full_path not in reverse:
            reverse[full_path] = alias
    return reverse


def aliases_for_prefix(prefix: str, alias_map: AliasMap) -> AliasMap:
    """Return the subset of *alias_map* whose full paths start with *prefix*."""
    return {
        alias: full_path
        for alias, full_path in alias_map.items()
        if full_path.startswith(prefix)
    }
