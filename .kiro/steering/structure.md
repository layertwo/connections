# Project Structure

## Directory Layout

```
connections/
├── src/connections/          # Main application package
│   ├── __init__.py
│   ├── main.py              # CLI interface and entry point
│   ├── model.py             # Data models (Flight, Coordinates)
│   └── map.py               # Map generation and visualization
├── tests/                   # Test suite
│   ├── conftest.py          # Pytest fixtures and configuration
│   ├── test_main.py         # CLI tests
│   ├── test_model.py        # Model tests
│   └── test_map.py          # Map generation tests
├── sample_flights.json      # Example flight data
├── pyproject.toml           # Project configuration and dependencies
└── README.md                # Documentation
```

## Module Organization

### src/connections/main.py
- CLI entry point using Click framework
- Command: `render` with options `-i`, `-o`, `-t`
- Handles JSON file reading and orchestrates Flight/FlightMap creation

### src/connections/model.py
- **Coordinates**: Dataclass for latitude/longitude
- **Flight**: Dataclass representing a flight route with IATA codes
  - Properties: `src_lat`, `src_lon`, `dst_lat`, `dst_lon`
  - Methods: `from_dict()`, `as_feature()` (GeoJSON)
  - Uses `@cached_property` for coordinate lookups
- **convert_airport_to_coords()**: LRU-cached function for IATA → coordinates conversion
- **Flights**: Type alias for `List[Flight]`

### src/connections/map.py
- **ImageFormat**: Enum for output formats (currently PNG only)
- **FlightMap**: Main visualization class
  - `draw()`: Generates Plotly figure with geo layout
  - `to_image()`: Converts figure to image bytes (LRU-cached)
  - `save()`: Writes image to file
  - Uses Natural Earth projection for global visualization

## Code Patterns

### Caching Strategy
- `@lru_cache()` on `convert_airport_to_coords()` to avoid repeated API lookups
- `@cached_property` on Flight coordinate properties
- `@lru_cache()` on `FlightMap.to_image()` for performance

### Testing Patterns
- Class-based test organization (`TestClassName`)
- Pytest fixtures for reusable test data
- Extensive mocking with `unittest.mock` and `pytest-mock`
- Click's `CliRunner` for CLI testing
- `tmp_path` fixture for file I/O tests
- Integration tests with real airport data where appropriate

### Import Organization
- Standard library imports first
- Third-party imports second
- Local imports last
- Sorted alphabetically within each group (isort enforced)
