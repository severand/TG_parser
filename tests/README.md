# Testing Suite

## Structure

- **unit/** - Unit tests for individual modules
- **integration/** - Integration tests
- **performance/** - Performance tests
- **mock_data/** - Mock data for testing

## Running Tests

### All tests
```bash
pytest tests/ -v
```

### Specific test file
```bash
pytest tests/unit/test_validators.py -v
```

### With coverage
```bash
pytest tests/ --cov=. --cov-report=html
```

### Performance tests
```bash
pytest tests/performance/ -v
```

## Writing Tests

```python
import pytest

def test_function():
    """Test description."""
    # Arrange
    data = {"key": "value"}
    
    # Act
    result = function(data)
    
    # Assert
    assert result is not None
```
