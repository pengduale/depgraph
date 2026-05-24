"""Lint a dependency graph for common structural issues."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set

from depgraph.analyzer import find_cycles


@dataclass
class LintIssue:
    code: str
    message: str
    nodes: List[str] = field(default_factory=list)


def lint_cycles(graph: Dict[str, List[str]]) -> List[LintIssue]:
    """Report every detected import cycle."""
    issues: List[LintIssue] = []
    for cycle in find_cycles(graph):
        issues.append(
            LintIssue(
                code="E001",
                message=f"Cycle detected: {' -> '.join(cycle)}",
                nodes=cycle,
            )
        )
    return issues


def lint_self_imports(graph: Dict[str, List[str]]) -> List[LintIssue]:
    """Report nodes that import themselves."""
    issues: List[LintIssue] = []
    for node, deps in graph.items():
        if node in deps:
            issues.append(
                LintIssue(
                    code="E002",
                    message=f"Self-import detected: {node}",
                    nodes=[node],
                )
            )
    return issues


def lint_missing_nodes(graph: Dict[str, List[str]]) -> List[LintIssue]:
    """Report dependency targets that have no entry in the graph."""
    known: Set[str] = set(graph.keys())
    issues: List[LintIssue] = []
    missing: Set[str] = set()
    for deps in graph.values():
        for dep in deps:
            if dep not in known and dep not in missing:
                missing.add(dep)
                issues.append(
                    LintIssue(
                        code="W001",
                        message=f"Dependency '{dep}' has no definition in graph",
                        nodes=[dep],
                    )
                )
    return issues


def run_linter(graph: Dict[str, List[str]]) -> List[LintIssue]:
    """Run all lint checks and return combined issue list."""
    issues: List[LintIssue] = []
    issues.extend(lint_cycles(graph))
    issues.extend(lint_self_imports(graph))
    issues.extend(lint_missing_nodes(graph))
    return issues


def format_issues(issues: List[LintIssue]) -> str:
    """Format lint issues into a human-readable string."""
    if not issues:
        return "No issues found."
    lines = []
    for issue in issues:
        lines.append(f"[{issue.code}] {issue.message}")
    return "\n".join(lines)
