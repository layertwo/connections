---
inclusion: always
---

# Project Structure & Architecture

## Module Responsibilities

### src/connections/main.py - CLI Entry Point
- Single `render` command with flags: `-i` (input), `-o` (output), `-t` (title)
- Reads JSON, creates Flight objects, instantiates FlightMap, saves output
- **When modifying**: Keep CLI logic thin; delegate to model/map modules

### src/connections/model.py - Data Layer
- **Coordinates**: Simple dataclass (lat, lon)
- **Flight**: Core domain model with IATA codes (src_iata, dst_iata)
  - Coordinate properties use `@cached_property` for lazy evaluation
  - `from_dict()` for JSON deserialization
  - `as_feature()` for GeoJSON conversion
- **convert_airport_to_coords()**: Cached IATA→coordinates lookup via airports-py
- **When modifying**: Maintain immutability of dataclasses; preserve caching decorators

### src/connections/map.py - Visualization Layer
- **FlightMap**: Encapsulates Plotly figure generation and export
  - `draw()`: Creates figure with geo layout (Natural Earth projection)
  - `to_image()`: Cached conversion to bytes (1920x1080 PNG)
  - `save()`: File I/O wrapper
- **When modifying**: Keep visualization logic isolated; maintain caching on `to_image()`

## Architecture Patterns

### Performance Optimization
- Use `@lru_cache()` for expensive external calls (airport lookups, image generation)
- Use `@cached_property` for derived data within objects
- **Rule**: Never remove caching without performance justification

### Data Flow
1. JSON → `Flight.from_dict()` → Flight objects
2. Flight objects → `FlightMap(flights)` → Plotly figure
3. Figure → `to_image()` → bytes → `save()` → PNG file
- **Rule**: Maintain unidirectional flow; avoid circular dependencies

### Error Handling
- Invalid IATA codes should raise clear exceptions from `convert_airport_to_coords()`
- File I/O errors should propagate with context
- **Rule**: Fail fast with descriptive messages; no silent failures

## Testing Architecture

### Test Organization
- One test file per module: `test_main.py`, `test_model.py`, `test_map.py`
- Class-based grouping: `class TestFlight`, `class TestFlightMap`
- **Rule**: Mirror source structure in tests; group related tests in classes

### Testing Patterns
- **CLI tests**: Use Click's `CliRunner` for command invocation
- **File I/O tests**: Use pytest's `tmp_path` fixture
- **External dependencies**: Mock airports-py and Plotly with `pytest-mock`
- **Integration tests**: Use real airport data for end-to-end validation
- **Rule**: Mock external APIs; use fixtures for reusable test data

### Fixtures (tests/conftest.py)
- Define shared test data (sample flights, coordinates)
- **Rule**: Add fixtures for data used in 3+ tests

## Code Style Conventions

### Import Order (isort enforced)
```python
# Standard library
import json
from pathlib import Path

# Third-party
import click
from plotly import graph_objects as go

# Local
from connections.model import Flight
```

### Type Hints
- Use dataclasses for structured data
- Define type aliases for clarity (`Flights = List[Flight]`)
- **Rule**: Add type hints to all public functions and methods

### Naming Conventions
- Functions: `snake_case` (e.g., `convert_airport_to_coords`)
- Classes: `PascalCase` (e.g., `FlightMap`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_WIDTH`)
- **Rule**: Follow PEP 8; use descriptive names over abbreviations

## File Modification Guidelines

### Adding New Features
1. Determine layer: CLI (main.py), data (model.py), or visualization (map.py)
2. Add implementation with appropriate caching
3. Add corresponding tests with mocks
4. Update type hints and docstrings

### Refactoring
- Preserve public APIs unless breaking change is justified
- Maintain test coverage above 80%
- Keep caching decorators intact
- **Rule**: Run `poetry run pytest --cov` before committing

### Dependencies
- Add via `poetry add <package>` (production) or `poetry add --group dev <package>` (development)
- **Rule**: Justify new dependencies; prefer stdlib when possible
