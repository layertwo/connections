---
inclusion: always
---

# Technology Stack & Development Standards

## Build System & Dependencies

**Package Manager**: Poetry (NEVER use `pip install`)
**Python Version**: 3.10+

### Critical Production Dependencies
- **plotly** (^6.3.0): Visualization via `graph_objects.Figure` and `graph_objects.Scattergeo`
- **airports-py** (^3.0.0): IATA→coordinates (external API - MUST mock in tests)
- **geojson** (^3.2.0): GeoJSON Feature generation
- **click** (^8.2.1): CLI framework
- **kaleido** (0.2.1): PNG export via `fig.to_image()`

### Development Dependencies
- **pytest** (^9.0.0): Test framework with class-based organization
- **pytest-mock** (^3.14.1): Use `mocker` fixture for external dependencies
- **pytest-cov** (^7.0.0): Minimum 80% coverage required
- **black** (^25.1.0): Auto-formatter (100 char line length)
- **isort** (^7.0.0): Import sorter (black profile)

## Mandatory Workflow Commands

**Before any code changes**:
```bash
poetry run pytest --cov=src/connections
```

**After any code changes**:
```bash
poetry run black src/ tests/ && poetry run isort src/ tests/
poetry run pytest --cov=src/connections
```

**Adding dependencies**:
```bash
poetry add <package>              # Production
poetry add --group dev <package>  # Development
```

## Code Quality Standards

### Formatting (Non-Negotiable)
- 100 character line length
- Black formatting (auto-applied)
- Import order: stdlib → third-party → local (isort auto-applied)
- Always run formatters after code generation

### Type Hints (Required)
All function signatures must include type hints:
```python
from typing import List, Dict, Optional
from dataclasses import dataclass

def convert_airport_to_coords(iata: str) -> Coordinates:
    ...
```

### Testing (Required)
- Minimum 80% coverage on all changes
- Test file mirrors source: `src/connections/model.py` → `tests/test_model.py`
- Use class-based test organization
- Mock external dependencies only (airports-py, plotly)
- Use `tmp_path` fixture for file I/O
- Define reusable fixtures in `conftest.py`

### Caching (Performance Critical)
**NEVER remove these without benchmarking**:
- `@lru_cache()`: Expensive function calls (airport lookups)
- `@cached_property`: Derived object properties (Flight coordinates)

## Import Template (Strict Order)
```python
# Standard library (alphabetical)
import json
from functools import lru_cache
from pathlib import Path

# Third-party (alphabetical)
import click
from plotly import graph_objects as go

# Local (alphabetical)
from connections.model import Flight
```

## Test Template
```python
import pytest
from click.testing import CliRunner

class TestFeature:
    def test_behavior(self, mocker, tmp_path):
        # Arrange: mock external dependencies
        mock_airport = mocker.patch("connections.model.airports.airport_by_iata")
        
        # Act
        result = function_under_test()
        
        # Assert
        assert result == expected
```

## Critical Rules for AI Assistants

### ALWAYS
1. Run formatters after generating code
2. Add tests for new functions/methods
3. Include type hints on all signatures
4. Use `pathlib.Path` for file operations
5. Mock external libraries (airports-py, plotly), not internal functions
6. Verify ≥80% coverage before completing tasks
7. Use Poetry for all dependency management

### NEVER
1. Remove `@lru_cache()` or `@cached_property` without justification
2. Use `pip install` (use `poetry add`)
3. Skip test coverage
4. Mock internal functions
5. Hardcode file paths

## New Function Checklist
1. Add type hints to signature
2. Add docstring if public API
3. Add caching decorator if expensive operation
4. Create test in `tests/test_<module>.py`
5. Run `poetry run black src/ tests/ && poetry run isort src/ tests/`
6. Run `poetry run pytest --cov=src/connections`
7. Verify coverage ≥80%
