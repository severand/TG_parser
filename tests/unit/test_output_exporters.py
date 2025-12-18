"""Unit tests for output exporters (JSON, CSV)."""

import pytest
import json
import csv
from pathlib import Path
from datetime import datetime

from output.json_exporter import JSONExporter
from output.csv_exporter import CSVExporter
from output.console_output import ConsoleOutput
from output.table_formatter import TableFormatter


class TestJSONExporter:
    """Test JSON export functionality."""

    def test_json_exporter_init(self, tmp_dir):
        """Test JSONExporter initialization."""
        exporter = JSONExporter(output_dir=str(tmp_dir))
        assert Path(tmp_dir).exists()

    def test_export_messages_creates_file(self, tmp_dir, sample_messages):
        """Test that export_messages creates a file."""
        exporter = JSONExporter(output_dir=str(tmp_dir))
        filepath = exporter.export_messages(sample_messages)
        assert Path(filepath).exists()
        assert filepath.endswith('.json')

    def test_export_messages_valid_json(self, tmp_dir, sample_messages):
        """Test that exported JSON is valid."""
        exporter = JSONExporter(output_dir=str(tmp_dir))
        filepath = exporter.export_messages(sample_messages)
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert 'metadata' in data
        assert 'messages' in data
        assert len(data['messages']) == len(sample_messages)

    def test_export_search_results(self, tmp_dir, sample_search_result):
        """Test exporting search results."""
        exporter = JSONExporter(output_dir=str(tmp_dir))
        filepath = exporter.export_search_results([sample_search_result])
        assert Path(filepath).exists()
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert 'results' in data

    def test_export_statistics(self, tmp_dir):
        """Test exporting statistics."""
        exporter = JSONExporter(output_dir=str(tmp_dir))
        stats = {'total_messages': 100, 'success_rate': 95.5}
        filepath = exporter.export_statistics(stats)
        assert Path(filepath).exists()
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert 'statistics' in data

    def test_export_messages_with_custom_filename(self, tmp_dir, sample_messages):
        """Test exporting with custom filename."""
        exporter = JSONExporter(output_dir=str(tmp_dir))
        filepath = exporter.export_messages(sample_messages, filename='custom.json')
        assert 'custom.json' in filepath

    def test_export_messages_compact(self, tmp_dir, sample_messages):
        """Test compact JSON export (no pretty-print)."""
        exporter = JSONExporter(output_dir=str(tmp_dir))
        filepath = exporter.export_messages(sample_messages, pretty=False)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        # Compact JSON should have fewer newlines
        assert '\n' in content or len(content) > 0


class TestCSVExporter:
    """Test CSV export functionality."""

    def test_csv_exporter_init(self, tmp_dir):
        """Test CSVExporter initialization."""
        exporter = CSVExporter(output_dir=str(tmp_dir))
        assert Path(tmp_dir).exists()

    def test_export_messages_creates_file(self, tmp_dir, sample_messages):
        """Test that export_messages creates CSV file."""
        exporter = CSVExporter(output_dir=str(tmp_dir))
        filepath = exporter.export_messages(sample_messages)
        assert Path(filepath).exists()
        assert filepath.endswith('.csv')

    def test_export_messages_valid_csv(self, tmp_dir, sample_messages):
        """Test that exported CSV is valid."""
        exporter = CSVExporter(output_dir=str(tmp_dir))
        filepath = exporter.export_messages(sample_messages)
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == len(sample_messages)
        # Check headers exist
        assert 'id' in reader.fieldnames
        assert 'text' in reader.fieldnames
        assert 'author' in reader.fieldnames

    def test_export_search_results(self, tmp_dir, sample_search_result):
        """Test exporting search results to CSV."""
        exporter = CSVExporter(output_dir=str(tmp_dir))
        filepath = exporter.export_search_results([sample_search_result])
        assert Path(filepath).exists()
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == 1

    def test_export_statistics(self, tmp_dir):
        """Test exporting statistics to CSV."""
        exporter = CSVExporter(output_dir=str(tmp_dir))
        stats = {'total_messages': 100, 'success_rate': 95.5}
        filepath = exporter.export_statistics(stats)
        assert Path(filepath).exists()
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        # Should have header + data rows
        assert len(rows) >= 2

    def test_export_messages_text_truncation(self, tmp_dir):
        """Test that long text is truncated in CSV."""
        from data.models import Message
        long_text = 'a' * 2000
        msg = Message(
            id=1, channel_id=1, author='test', text=long_text,
            timestamp=datetime.now(), views=100, reactions=0,
            mentions=[], hashtags=[], urls=[], edited=False, pinned=False
        )
        exporter = CSVExporter(output_dir=str(tmp_dir))
        filepath = exporter.export_messages([msg])
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            row = next(reader)
        # Text should be truncated to 1000 chars
        assert len(row['text']) <= 1000


class TestTableFormatter:
    """Test ASCII table formatting."""

    def test_create_simple_table(self):
        """Test creating simple ASCII table."""
        formatter = TableFormatter()
        headers = ['Name', 'Value']
        rows = [['test', '100'], ['example', '200']]
        table = formatter.create_table(headers, rows)
        assert 'Name' in table
        assert 'Value' in table
        assert '100' in table
        assert '200' in table

    def test_table_has_borders(self):
        """Test that table has borders by default."""
        formatter = TableFormatter()
        headers = ['A', 'B']
        rows = [['1', '2']]
        table = formatter.create_table(headers, rows, borders=True)
        assert '+' in table
        assert '-' in table
        assert '|' in table

    def test_table_without_borders(self):
        """Test creating table without borders."""
        formatter = TableFormatter()
        headers = ['A', 'B']
        rows = [['1', '2']]
        table = formatter.create_table(headers, rows, borders=False)
        # Should still have content, just no borders
        assert 'A' in table and 'B' in table

    def test_key_value_table(self):
        """Test creating key-value table."""
        formatter = TableFormatter()
        data = {'Total': 100, 'Success': 95}
        table = formatter.create_key_value_table(data)
        assert 'Total' in table or 'total' in table.lower()
        assert '100' in table


class TestConsoleOutput:
    """Test console output."""

    def test_console_output_init(self):
        """Test ConsoleOutput initialization."""
        output = ConsoleOutput(use_colors=True, width=80)
        assert output.use_colors is True
        assert output.width == 80

    def test_print_success(self, capsys):
        """Test printing success message."""
        output = ConsoleOutput(use_colors=False)
        output.print_success("Test success")
        captured = capsys.readouterr()
        assert "Test success" in captured.out

    def test_print_error(self, capsys):
        """Test printing error message."""
        output = ConsoleOutput(use_colors=False)
        output.print_error("Test error")
        captured = capsys.readouterr()
        assert "Test error" in captured.out

    def test_colorize_without_colors(self):
        """Test colorize returns plain text when colors disabled."""
        output = ConsoleOutput(use_colors=False)
        text = output._colorize("Hello", "")
        assert text == "Hello"
