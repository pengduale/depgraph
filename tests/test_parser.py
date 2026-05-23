"""Tests for depgraph.parser module."""

import textwrap
import tempfile
import os
from pathlib import Path

import pytest

from depgraph.parser import extract_imports, build_dependency_graph


def write_file(directory: str, relative_path: str, content: str) -> str:
    full_path = Path(directory) / relative_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(textwrap.dedent(content))
    return str(full_path)


def test_extract_imports_simple():
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write("import os\nimport sys\n")
        name = f.name
    try:
        result = extract_imports(name)
        assert "os" in result
        assert "sys" in result
    finally:
        os.unlink(name)


def test_extract_imports_from_style():
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write("from pathlib import Path\nfrom collections import defaultdict\n")
        name = f.name
    try:
        result = extract_imports(name)
        assert "pathlib" in result
        assert "collections" in result
    finally:
        os.unlink(name)


def test_extract_imports_syntax_error():
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write("def broken(:\n    pass\n")
        name = f.name
    try:
        result = extract_imports(name)
        assert result == []
    finally:
        os.unlink(name)


def test_build_dependency_graph():
    with tempfile.TemporaryDirectory() as tmpdir:
        write_file(tmpdir, "alpha/__init__.py", "")
        write_file(tmpdir, "alpha/core.py", "import beta\n")
        write_file(tmpdir, "beta/__init__.py", "")
        write_file(tmpdir, "beta/utils.py", "import alpha\n")

        graph = build_dependency_graph(tmpdir)

        assert "alpha/core" in graph or any("core" in k for k in graph)
        # At least one cross-module dependency should be detected
        all_deps = set()
        for deps in graph.values():
            all_deps.update(deps)
        assert "beta" in all_deps or "alpha" in all_deps


def test_build_dependency_graph_empty_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        graph = build_dependency_graph(tmpdir)
        assert graph == {}
