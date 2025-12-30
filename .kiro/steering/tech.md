---
inclusion: always
---

# Technology Stack & Development Workflow

## Build System

- **Package Manager**: Poetry (all dependency management must use Poetry commands)
- **Python Version**: 3.10+ (ensure compatibility when suggesting code)
- **Build Backend**: poetry-core

## Critical Dependencies & Their Roles

### Production Dependencies
- **plotly** (^6.3.0): Map visualization via `graph_objects.Figure` and `graph_objects.Scattergeo`
- **airports-py** (^3.0.0): IATA code → coordinates conversion (external data source, must be mocked in tests)
- **geojson** (^3.2.0): GeoJSON Feature generation for flight routes
- **click** (^8.2.1): CLI framework (use `@click.command()` and `CliRunner` for testing)
- **kaleido** (0.2.1): PNG export from Plotly figures (use `fig.to_image()`)

### Development Dependencies
- **pytest** (^9.0.0): Test framework (use class-based test organization)
- **pytest-mock** (^3.14.1): Mocking (use `mocker` fixture for external dependencies)
- **pytest-cov** (^7.0.0): Coverage reporting (80% minimum required)
- **black** (^25.1.0): Auto-formatter (100 char line length)
- **isort** (^7.0.0): Import sorter (black profile, 100 char line length)

## Essential Commands

### Before Making Changes
```bash
poetry run pytest --cov=src/connections  # Verify tests pass and coverage ≥80%
```

### After Code Changes
```bash
poetry run black src/ tests/ && poetry run isort src/ tests/  # Format code
poetry run pytest --cov=src/connections                       # Verify changes
```

### Adding Dependencies
```bash
poetry add <package>                    # Production dependency
poetry add --group dev <package>        # Development dependency
```

### Running the Application
```bash
poetry run connections -i INPUT_FILE -o OUTPUT_FILE -t TITLE
```

## Code Quality Rules for AI Assistants

### Formatting (Auto-enforced)
- **Line length**: 100 characters maximum
- **Import order**: stdlib → third-party → local (isort handles this)
- **Style**: Black formatting (no manual formatting needed)
- **Action**: Always run `black` and `isort` after code generation

### Testing Requirements
- **Coverage**: Maintain ≥80% code coverage on all changes
- **Test location**: `tests/test_<module>.py` mirrors `src/connections/<module>.py`
- **Mocking**: Mock `airports.airport_by_iata()` and `plotly` figure methods
- **Fixtures**: Use `tmp_path` for file I/O, define reusable data in `conftest.py`
- **Action**: Add tests for any new functions/methods; run pytest before completing tasks

### Type Hints
- Add type hints to all function signatures
- Use `from typing import List, Dict, Optional` as needed
- Dataclasses should have typed fields
- **Action**: Include type hints in all generated code

### Dependency Management
- Never suggest `pip install` (use `poetry add` instead)
- Justify new dependencies (prefer stdlib when possible)
- Check `pyproject.toml` before adding existing dependencies
- **Action**: Use Poetry commands exclusively for package management

## Common Pitfalls to Avoid

1. **Don't remove caching decorators** (`@lru_cache`, `@cached_property`) without justification
2. **Don't mock internal functions** (only mock external libraries like airports-py)
3. **Don't use `pip`** (Poetry manages the virtual environment)
4. **Don't skip test coverage** (changes without tests will be rejected)
5. **Don't hardcode file paths** (use `pathlib.Path` for cross-platform compatibility)

## Quick Reference for Code Generation

### Import Template
```python
# Standard library
import json
from functools import lru_cache
from pathlib import Path

# Third-party
import click
from plotly import graph_objects as go

# Local
from connections.model import Flight
```

### Test Template
```python
import pytest
from click.testing import CliRunner

class TestFeature:
    def test_behavior(self, mocker, tmp_path):
        # Arrange: mock external dependencies
        mock_airport = mocker.patch("connections.model.airports.airport_by_iata")
        
        # Act: execute code
        result = function_under_test()
        
        # Assert: verify behavior
        assert result == expected
```

### Adding a New Function Checklist
1. Add type hints to signature
2. Add docstring if public API
3. Use appropriate caching decorator if expensive
4. Create corresponding test in `tests/test_<module>.py`
5. Run `black`, `isort`, and `pytest --cov`
6. Verify coverage remains ≥80%
