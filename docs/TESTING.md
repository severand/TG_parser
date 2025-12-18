# Testing Guide for TG Parser

## Overview

TG Parser uses **pytest** as the testing framework with comprehensive unit and integration tests.

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── unit/                    # Unit tests
│   ├── test_message_processor.py
│   ├── test_search_engine.py
│   ├── test_parser.py
│   ├── test_validators.py
│   ├── test_stats_collector.py
│   └── test_output_exporters.py
├── integration/             # Integration tests
│   └── test_integration_parser.py
└── performance/             # Performance tests (planned)
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/unit/test_message_processor.py
```

### Run Specific Test Class

```bash
pytest tests/unit/test_message_processor.py::TestMessageProcessorTextExtraction
```

### Run Specific Test

```bash
pytest tests/unit/test_message_processor.py::TestMessageProcessorTextExtraction::test_extract_text_simple
```

### Run with Markers

```bash
# Only unit tests
pytest -m unit

# Only integration tests
pytest -m integration

# Only performance tests
pytest -m performance

# Skip slow tests
pytest -m "not slow"
```

## Code Coverage

### Generate Coverage Report

```bash
pytest --cov=core --cov=network --cov=utils --cov=data --cov=stats --cov=output
```

### Generate HTML Coverage Report

```bash
pytest --cov=core --cov-report=html
# Open htmlcov/index.html in browser
```

### Check Coverage Against Threshold

```bash
pytest --cov=core --cov-fail-under=80
```

## Test Categories

### Unit Tests

**Location:** `tests/unit/`

**Focus:** Individual function/class testing

**Examples:**
- Text extraction from HTML
- Keyword search logic
- Statistics calculations
- Data validation

**Speed:** Fast (~1-5ms per test)

```bash
pytest tests/unit/ -v
```

### Integration Tests

**Location:** `tests/integration/`

**Focus:** Component interaction and data flow

**Examples:**
- Parse and search workflow
- Message processing pipeline
- Search with multiple filters
- Error handling between components

**Speed:** Medium (~10-100ms per test)

```bash
pytest tests/integration/ -v
```

### Performance Tests

**Location:** `tests/performance/`

**Focus:** Performance benchmarks and optimization

**Examples:**
- Parsing speed with 1000+ messages
- Search performance on large datasets
- Memory usage patterns

**Speed:** Slow (may take seconds)

```bash
pytest tests/performance/ -v --timeout=300
```

## Fixtures

Common fixtures are defined in `tests/conftest.py`:

### `sample_message`

Single sample Message object:

```python
def test_something(sample_message):
    assert sample_message.id == 1
```

### `sample_messages`

List of 5 sample Message objects:

```python
def test_something(sample_messages):
    assert len(sample_messages) == 5
```

### `sample_channel`

Channel metadata dictionary:

```python
def test_something(sample_channel):
    assert sample_channel['username'] == 'test_channel'
```

### `sample_search_result`

Single SearchResult object:

```python
def test_something(sample_search_result):
    assert sample_search_result.relevance_score > 0
```

### `sample_html`

Sample HTML for parsing:

```python
def test_something(sample_html):
    text = MessageProcessor.extract_text(sample_html)
    assert len(text) > 0
```

### `stats_collector`

StatsCollector instance:

```python
def test_something(stats_collector):
    stats_collector.add_message(msg)
    assert stats_collector.total_messages == 1
```

### `parser_instance`

Parser instance with max_workers=2:

```python
def test_something(parser_instance):
    assert parser_instance.max_workers == 2
```

### `tmp_dir`

Temporary directory (cleaned up after test):

```python
def test_something(tmp_dir):
    filepath = tmp_dir / 'test.txt'
    filepath.write_text('test')
    assert filepath.exists()
    # Auto-cleaned after test
```

## Writing Tests

### Basic Unit Test

```python
from core.message_processor import MessageProcessor

class TestMessageProcessor:
    def test_extract_text(self):
        """Test extracting text from HTML."""
        html = "<p>Hello World</p>"
        text = MessageProcessor.extract_text(html)
        assert text == "Hello World"
```

### Test with Fixtures

```python
def test_search_with_messages(sample_messages):
    """Test searching through messages."""
    engine = SearchEngine()
    results = engine.search(sample_messages, ['test'])
    assert len(results) >= 0
```

### Test with Mocking

```python
from unittest.mock import patch

def test_with_mock():
    """Test using mock objects."""
    with patch('core.parser.Parser.parse_channels') as mock:
        mock.return_value = []
        parser = Parser()
        result = parser.parse_channels(['@channel'])
        assert result == []
```

### Parametrized Tests

```python
import pytest

@pytest.mark.parametrize("keyword,expected", [
    ("test", True),
    ("python", True),
    ("xyz", False),
])
def test_search_keywords(sample_messages, keyword, expected):
    """Test various keywords."""
    engine = SearchEngine()
    results = engine.search(sample_messages, [keyword])
    has_results = len(results) > 0
    assert has_results == expected
```

## Test Markers

### Mark Test as Unit

```python
@pytest.mark.unit
def test_something():
    pass
```

### Mark Test as Integration

```python
@pytest.mark.integration
def test_something():
    pass
```

### Mark Test as Slow

```python
@pytest.mark.slow
def test_something():
    pass
```

### Skip Test in CI

```python
@pytest.mark.skip_ci
def test_something():
    pass
```

## Configuration

Test configuration is in `pytest.ini`:

```ini
[pytest]
addopts = -v --cov=core --cov-report=html
testpaths = tests
markers =
    unit: Unit tests
    integration: Integration tests
```

## Best Practices

### 1. Use Descriptive Names

✅ Good:
```python
def test_extract_text_removes_scripts():
    pass
```

❌ Bad:
```python
def test_1():
    pass
```

### 2. Test One Thing Per Test

✅ Good:
```python
def test_search_returns_list():
    engine = SearchEngine()
    results = engine.search([msg], ['test'])
    assert isinstance(results, list)

def test_search_results_sorted():
    engine = SearchEngine()
    results = engine.search([msg], ['test'])
    assert results[0].score >= results[1].score
```

❌ Bad:
```python
def test_search():
    engine = SearchEngine()
    results = engine.search([msg], ['test'])
    assert isinstance(results, list)
    assert results[0].score >= results[1].score
```

### 3. Use Fixtures for Setup

✅ Good:
```python
def test_something(sample_messages):
    assert len(sample_messages) == 5
```

❌ Bad:
```python
def test_something():
    messages = [Message(...), Message(...), ...]
    assert len(messages) == 5
```

### 4. Use Assertions, Not Exceptions

✅ Good:
```python
assert validate_email('test@example.com') is True
```

❌ Bad:
```python
try:
    validate_email('test@example.com')
except Exception:
    assert False
```

## Continuous Integration

Tests are run automatically on:
- Push to any branch
- Pull requests
- Scheduled nightly runs

### GitHub Actions Configuration

See `.github/workflows/tests.yml`

## Coverage Goals

- **Overall:** ≥ 80%
- **Core modules:** ≥ 90%
- **Utils:** ≥ 85%
- **Data models:** ≥ 80%

## Troubleshooting

### Test Fails Locally But Passes in CI

1. Check Python version (should be 3.11+)
2. Verify all dependencies installed: `pip install -r requirements.txt`
3. Clear cache: `pytest --cache-clear`
4. Run in isolation: `pytest -p no:cache tests/unit/test_file.py`

### Test Hangs or Timeout

1. Add timeout: `pytest --timeout=10`
2. Check for infinite loops
3. Verify mocks are set up correctly
4. Look for blocking I/O operations

### Mock Not Working

```python
# Correct:
with patch('module.function') as mock:
    mock.return_value = value

# Incorrect - patch before import:
# from module import function  # Too late!
with patch('module.function') as mock:
    pass
```

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [Coverage.py](https://coverage.readthedocs.io/)

---

**Last Updated:** 2025-12-18
