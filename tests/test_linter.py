"""Tests for depgraph.linter."""
from __future__ import annotations

import pytest

from depgraph.linter import (
    LintIssue,
    format_issues,
    lint_cycles,
    lint_missing_nodes,
    lint_self_imports,
    run_linter,
)


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
    }


def test_lint_cycles_clean_graph(clean_graph):
    assert lint_cycles(clean_graph) == []


def test_lint_cycles_detects_cycle(cycle_graph):
    issues = lint_cycles(cycle_graph)
    assert len(issues) == 1
    assert issues[0].code == "E001"
    assert "Cycle" in issues[0].message


def test_lint_self_imports_none(clean_graph):
    assert lint_self_imports(clean_graph) == []


def test_lint_self_imports_detected():
    graph = {"a": ["a", "b"], "b": []}
    issues = lint_self_imports(graph)
    assert len(issues) == 1
    assert issues[0].code == "E002"
    assert "a" in issues[0].nodes


def test_lint_missing_nodes_none(clean_graph):
    assert lint_missing_nodes(clean_graph) == []


def test_lint_missing_nodes_detects_unknown():
    graph = {"a": ["b", "external"], "b": []}
    issues = lint_missing_nodes(graph)
    assert len(issues) == 1
    assert issues[0].code == "W001"
    assert "external" in issues[0].message


def test_lint_missing_nodes_no_duplicate_reports():
    graph = {"a": ["ghost"], "b": ["ghost"]}
    issues = lint_missing_nodes(graph)
    assert len(issues) == 1


def test_run_linter_combines_all_checks():
    graph = {
        "a": ["a"],       # self-import
        "b": ["missing"],  # missing node
    }
    issues = run_linter(graph)
    codes = {i.code for i in issues}
    assert "E002" in codes
    assert "W001" in codes


def test_format_issues_empty():
    assert format_issues([]) == "No issues found."


def test_format_issues_non_empty():
    issues = [
        LintIssue(code="E001", message="Cycle detected: a -> b", nodes=["a", "b"]),
        LintIssue(code="W001", message="Dependency 'x' has no definition", nodes=["x"]),
    ]
    output = format_issues(issues)
    assert "[E001]" in output
    assert "[W001]" in output
    assert "Cycle" in output


def test_lint_issue_nodes_default_empty():
    issue = LintIssue(code="E001", message="test")
    assert issue.nodes == []
