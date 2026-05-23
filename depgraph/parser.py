"""Parse Python source files to extract import dependencies."""

import ast
import os
from pathlib import Path
from typing import Dict, List, Set


def extract_imports(filepath: str) -> List[str]:
    """Extract all imported module names from a Python source file."""
    imports: List[str] = []
    try:
        source = Path(filepath).read_text(encoding="utf-8")
        tree = ast.parse(source, filename=filepath)
    except (SyntaxError, OSError):
        return imports

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:
                imports.append(node.module.split(".")[0])

    return list(set(imports))


def build_dependency_graph(root_dir: str) -> Dict[str, Set[str]]:
    """Walk a directory and build a dependency graph for all Python files.

    Returns a dict mapping module name -> set of imported module names.
    Only includes edges where the imported module also exists in the project.
    """
    root = Path(root_dir).resolve()
    module_files: Dict[str, str] = {}

    for py_file in root.rglob("*.py"):
        relative = py_file.relative_to(root)
        parts = list(relative.with_suffix("").parts)
        module_name = ".".join(parts)
        module_files[module_name] = str(py_file)

    # Build top-level module name lookup for filtering
    top_level_modules: Set[str] = {name.split(".")[0] for name in module_files}

    graph: Dict[str, Set[str]] = {name: set() for name in module_files}

    for module_name, filepath in module_files.items():
        imports = extract_imports(filepath)
        for imp in imports:
            if imp in top_level_modules and imp != module_name.split(".")[0]:
                graph[module_name].add(imp)

    return graph
