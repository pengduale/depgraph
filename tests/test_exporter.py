"""Tests for depgraph.exporter module."""

import json
import os
import pytest

from depgraph.exporter import export_json, export_dot, save_export


SAMPLE_GRAPH = {
    'myapp.main': {'myapp.utils', 'myapp.models'},
    'myapp.utils': {'os', 'sys'},
    'myapp.models': set(),
}


def test_export_json_structure():
    result = export_json(SAMPLE_GRAPH)
    data = json.loads(result)
    assert 'myapp.main' in data
    assert 'myapp.utils' in data
    assert 'myapp.models' in data


def test_export_json_deps_are_sorted_lists():
    result = export_json(SAMPLE_GRAPH)
    data = json.loads(result)
    assert data['myapp.main'] == ['myapp.models', 'myapp.utils']
    assert data['myapp.utils'] == ['os', 'sys']
    assert data['myapp.models'] == []


def test_export_json_empty_graph():
    result = export_json({})
    assert json.loads(result) == {}


def test_export_json_custom_indent():
    result = export_json({'a': {'b'}}, indent=4)
    assert '    ' in result


def test_export_dot_contains_digraph():
    result = export_dot(SAMPLE_GRAPH)
    assert 'digraph' in result
    assert 'rankdir=LR' in result


def test_export_dot_contains_nodes():
    result = export_dot(SAMPLE_GRAPH)
    assert '"myapp.main"' in result
    assert '"myapp.utils"' in result
    assert '"myapp.models"' in result


def test_export_dot_contains_edges():
    result = export_dot(SAMPLE_GRAPH)
    assert '"myapp.main" -> "myapp.models"' in result
    assert '"myapp.main" -> "myapp.utils"' in result
    assert '"myapp.utils" -> "os"' in result


def test_export_dot_custom_graph_name():
    result = export_dot({}, graph_name='my_project')
    assert 'digraph "my_project"' in result


def test_export_dot_closes_brace():
    result = export_dot(SAMPLE_GRAPH)
    assert result.strip().endswith('}')


def test_save_export_writes_file(tmp_path):
    output_file = tmp_path / 'graph.json'
    content = '{"a": ["b"]}'
    save_export(content, str(output_file))
    assert output_file.exists()
    assert output_file.read_text(encoding='utf-8') == content


def test_save_export_overwrites_existing(tmp_path):
    output_file = tmp_path / 'graph.dot'
    output_file.write_text('old content', encoding='utf-8')
    save_export('new content', str(output_file))
    assert output_file.read_text(encoding='utf-8') == 'new content'
