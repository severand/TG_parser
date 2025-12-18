# Development Guide - Telegram Parser Pro

## Project Structure

See `2.-PROJECT-STRUCTURE.md` for detailed architecture.

## Module Organization

```
telegram_parser/
├── config/           # Configuration layer
├── core/             # Main parser logic
├── network/          # Network requests
├── utils/            # Utilities
├── data/             # Data models and storage
├── stats/            # Statistics collector
├── output/           # Output formatters
├── tests/            # Test suite
└── docs/             # Documentation
```

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/my-feature
```

### 2. Write Code

- Follow PEP 8 style guide
- Add type hints
- Add docstrings
- Write unit tests

### 3. Format Code

```bash
black . --line-length=100
isort .
pylint core/ network/ utils/ data/ stats/ output/
```

### 4. Run Tests

```bash
pytest tests/ -v --cov=. --cov-report=html
```

### 5. Commit and Push

```bash
git add .
git commit -m "feat: description of changes"
git push origin feature/my-feature
```

### 6. Create Pull Request

Open PR in GitHub with description of changes.

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test File

```bash
pytest tests/unit/test_config_loader.py -v
```

### Run with Coverage

```bash
pytest tests/ --cov=. --cov-report=html
```

## Code Quality

### Linting

```bash
pylint core/ network/ utils/ data/ stats/ output/
flake8 .
```

### Type Checking

```bash
mypy . --ignore-missing-imports
```

### Formatting

```bash
black . --line-length=100
isort .
```

## Adding New Modules

1. Create module directory in appropriate layer
2. Add `__init__.py`
3. Implement module with type hints
4. Add unit tests in `tests/unit/`
5. Add integration tests if applicable
6. Update documentation

## Module Interface Template

```python
"""Module description."""

from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class MyModel:
    """Data model for module."""
    id: str
    name: str


class MyService:
    """Main service class."""

    def __init__(self, config: Dict) -> None:
        """Initialize service.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config

    def do_something(self, item: MyModel) -> Optional[str]:
        """Do something with item.
        
        Args:
            item: Input model
            
        Returns:
            Result string or None
        """
        pass
```

## Git Commit Messages

Follow conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `refactor:` Code refactoring
- `test:` Test additions/changes
- `docs:` Documentation updates
- `chore:` Build, deps, etc.

## Debugging

### Print Debugging

```python
from utils.logger import Logger

logger = Logger()
logger.debug(f"Variable value: {variable}")
```

### Using Debugger

```python
import pdb; pdb.set_trace()
```

Or use VS Code debugger with `launch.json`.

## Performance

### Profile Code

```bash
python -m cProfile -s cumulative main.py
```

### Memory Profiler

```bash
python -m memory_profiler main.py
```

## Documentation

Write docstrings for all functions:

```python
def function(arg1: str, arg2: int) -> bool:
    """Short description.
    
    Longer description if needed.
    
    Args:
        arg1: First argument
        arg2: Second argument
        
    Returns:
        Boolean result
        
    Raises:
        ValueError: If validation fails
    """
    pass
```
