# depgraph

Visualizes dependency graphs for Python projects as interactive SVG diagrams.

---

## Installation

```bash
pip install depgraph
```

Or install from source:

```bash
git clone https://github.com/yourname/depgraph.git
cd depgraph && pip install -e .
```

---

## Usage

Point `depgraph` at any Python project directory to generate an interactive SVG dependency graph:

```bash
depgraph ./my_project --output graph.svg
```

You can also use it programmatically:

```python
from depgraph import DependencyGraph

graph = DependencyGraph("./my_project")
graph.render("graph.svg")
```

Open the resulting `graph.svg` in any browser to explore dependencies interactively — hover over nodes to highlight connections, and click to expand or collapse modules.

### Options

| Flag | Description |
|------|-------------|
| `--output` | Output file path (default: `graph.svg`) |
| `--depth` | Max dependency depth to traverse (default: `3`) |
| `--exclude` | Comma-separated list of modules to exclude |

---

## Requirements

- Python 3.8+
- [Graphviz](https://graphviz.org/) must be installed on your system

---

## License

This project is licensed under the [MIT License](LICENSE).