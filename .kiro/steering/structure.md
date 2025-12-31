---
inclusion: always
---
---
inclusion: always
---

# Project Structure & Architecture

## Module Responsibilities

### src/connections/main.py - CLI Entry Point
**Purpose**: Single `render` command orchestrating the entire pipeline

**Key Functions**:
- Parses CLI flags: `-i` (input), `-o` (output), `-t` (title)
- Reads JSON → creates Flight objects → instantiates FlightMap → saves PNG

**Modification Rules**:
- Keep CLI logic thin (orchestration only)
- Delegate business logic to model.py and map.py
- Use Click's `@click.command()` decorator pattern

### src/connections/model.py - Data Layer
**Purpose**: Domain models and coordinate conversion

**Key Components**:
- `Coordinates`: Dataclass with `lat` and `lon` fields
- `Flight`: Core model with `src_iata` and `dst_iata` fields
  - Uses `@cached_property` for coordinate lookups (lazy evaluation)
  - `from_dict()`: JSON deserialization
  - `as_feature()`: GeoJSON conversion
- `convert_airport_to_coords()`: IATA→coordinates via airports-py (cached with `@lru_cache()`)

**Modification Rules**:
- Dataclasses must remain immutable
- Never remove `@cached_property` or `@lru_cache()` decorators (performance critical)
- All coordinate lookups must go through `convert_airport_to_coords()`

### src/connections/map.py - Visualization Layer
**Purpose**: Plotly figure generation and PNG export

**Key Components**:
- `FlightMap`: Encapsulates visualization logic
  - `draw()`: Creates Plotly figure with Natural Earth projection
  - `to_image()`: Converts figure to PNG bytes (1920x1080, cached)
  - `save()`: Writes bytes to file

**Modification Rules**:
- Keep visualization logic isolated from data models
- Maintain caching on `to_image()` (expensive operation)
- PNG resolution fixed at 1920x1080

## Architecture Patterns

### Layered Architecture
```
CLI Layer (main.py) → Data Layer (model.py) → Visualization Layer (map.py)
```
- **Unidirectional flow**: CLI → Model → Map → Output
- **No circular dependencies**: Lower layers never import upper layers
- **Separation of concerns**: Each module has single responsibility

### Performance Optimization Strategy
**Critical**: This application makes expensive external calls and rendering operations

**Caching Requirements**:
- `@lru_cache()`: Use for expensive function calls (airport lookups, image generation)
- `@cached_property`: Use for derived object properties (Flight coordinates)

**Never Remove Caching Without**:
- Performance benchmarks showing it's unnecessary
- Explicit justification in code comments

### Data Flow Pipeline
```
JSON file → Flight.from_dict() → Flight objects → FlightMap(flights) → 
Plotly figure → to_image() → PNG bytes → save() → PNG file
```

**Rules**:
- Each step transforms data without side effects
- Errors propagate immediately (fail fast)
- No intermediate state stored globally

### Error Handling Philosophy
- **Fail fast**: Invalid IATA codes raise exceptions immediately
- **Clear messages**: Include context (e.g., "Invalid IATA code 'XYZ' in flight 3")
- **No silent failures**: All errors must be visible to user
- **Propagate with context**: File I/O errors include file paths

## Testing Architecture

### Test Organization
**Structure**: Mirror source code structure
```
src/connections/main.py    → tests/test_main.py
src/connections/model.py   → tests/test_model.py
src/connections/map.py     → tests/test_map.py
```

**Grouping**: Use classes to group related tests
```python
class TestFlight:
    def test_from_dict(self): ...
    def test_coordinates_cached(self): ...
```

### Testing Patterns by Layer

**CLI Tests** (test_main.py):
- Use Click's `CliRunner` for command invocation
- Test with `tmp_path` fixture for file I/O
- Mock both model and map layers

**Model Tests** (test_model.py):
- Mock `airports.airport_by_iata()` (external dependency)
- Verify caching behavior with repeated calls
- Test error handling for invalid IATA codes

**Map Tests** (test_map.py):
- Mock Plotly figure methods (`fig.to_image()`)
- Verify caching on `to_image()` method
- Test with `tmp_path` for file output

### Mocking Strategy
**Mock External Dependencies Only**:
- ✅ Mock: `airports.airport_by_iata()` (external library)
- ✅ Mock: `plotly.graph_objects.Figure.to_image()` (slow operation)
- ❌ Don't Mock: Internal functions (test real behavior)

**Fixture Usage** (tests/conftest.py):
- Define fixtures for data used in 3+ tests
- Common fixtures: sample flights, coordinates, mock airport data

### Coverage Requirements
- Minimum 80% coverage on all changes
- Run `poetry run pytest --cov=src/connections` before committing
- Add tests for any new functions/methods

## Code Style Conventions

### Import Order (isort with black profile)
```python
# Standard library (alphabetical)
import json
from pathlib import Path

# Third-party (alphabetical)
import click
from plotly import graph_objects as go

# Local (alphabetical)
from connections.model import Flight
```

### Type Hints
**Required**: All public functions and methods must have type hints

**Patterns**:
```python
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class Coordinates:
    lat: float
    lon: float

def convert_airport_to_coords(iata: str) -> Coordinates:
    ...

Flights = List[Flight]  # Type alias for clarity
```

### Naming Conventions (PEP 8)
- Functions/methods: `snake_case` (e.g., `convert_airport_to_coords`)
- Classes: `PascalCase` (e.g., `FlightMap`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_WIDTH`)
- Private: `_leading_underscore` (e.g., `_internal_helper`)

**Prefer descriptive names over abbreviations**: `coordinates` not `coords`, `destination` not `dst`

## Modification Workflows

### Adding New Features
1. **Identify layer**: CLI (main.py), data (model.py), or visualization (map.py)
2. **Implement with caching**: Add `@lru_cache()` or `@cached_property` if expensive
3. **Add type hints**: All function signatures must be typed
4. **Write tests**: Add to corresponding test file with appropriate mocks
5. **Format code**: Run `poetry run black src/ tests/ && poetry run isort src/ tests/`
6. **Verify coverage**: Run `poetry run pytest --cov=src/connections`

### Refactoring Existing Code
**Before Refactoring**:
- Run `poetry run pytest --cov` to establish baseline
- Identify public APIs that must remain stable

**During Refactoring**:
- Preserve caching decorators unless benchmarked
- Maintain test coverage ≥80%
- Keep public APIs stable (breaking changes require justification)

**After Refactoring**:
- Run `poetry run black src/ tests/ && poetry run isort src/ tests/`
- Run `poetry run pytest --cov=src/connections`
- Verify all tests pass and coverage maintained

### Adding Dependencies
**Process**:
```bash
poetry add <package>                    # Production
poetry add --group dev <package>        # Development
```

**Requirements**:
- Justify why stdlib is insufficient
- Check `pyproject.toml` to avoid duplicates
- Update tests to mock new external dependencies

## Quick Reference for AI Assistants

### Before Making Changes
```bash
poetry run pytest --cov=src/connections  # Verify baseline
```

### After Making Changes
```bash
poetry run black src/ tests/ && poetry run isort src/ tests/  # Format
poetry run pytest --cov=src/connections                       # Verify
```

### Common Pitfalls to Avoid
1. ❌ Removing `@lru_cache()` or `@cached_property` decorators
2. ❌ Mocking internal functions (only mock external libraries)
3. ❌ Using `pip install` instead of `poetry add`
4. ❌ Skipping tests for new functionality
5. ❌ Hardcoding file paths (use `pathlib.Path`)
6. ❌ Creating circular dependencies between modules