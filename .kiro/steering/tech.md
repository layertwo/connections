# Technology Stack

## Build System

- **Package Manager**: Poetry
- **Python Version**: 3.10+
- **Build Backend**: poetry-core

## Core Dependencies

- **plotly** (^6.3.0): Interactive map visualization and chart generation
- **airports-py** (^3.0.0): Airport data and coordinate lookup by IATA code
- **geojson** (^3.2.0): Geographic data format handling
- **click** (^8.2.1): Command-line interface framework
- **kaleido** (0.2.1): Static image export for Plotly charts

## Development Dependencies

- **pytest** (^9.0.0): Testing framework
- **pytest-mock** (^3.14.1): Mocking support for tests
- **pytest-cov** (^7.0.0): Code coverage reporting
- **black** (^25.1.0): Code formatting (line length: 100)
- **isort** (^7.0.0): Import sorting (black profile, line length: 100)

## Common Commands

### Installation
```bash
poetry install              # Install production dependencies
poetry install --with dev   # Install with development dependencies
```

### Running the Application
```bash
poetry run connections -i INPUT_FILE -o OUTPUT_FILE -t TITLE
```

### Testing
```bash
poetry run pytest                                    # Run all tests
poetry run pytest --cov=src/connections             # Run with coverage
poetry run pytest --cov-report=html                 # Generate HTML coverage report
```

### Code Formatting
```bash
poetry run black src/ tests/                        # Format code
poetry run isort src/ tests/                        # Sort imports
poetry run black src/ tests/ && poetry run isort src/ tests/  # Format and sort
```

## Code Quality Standards

- **Coverage Requirement**: Minimum 80% code coverage (enforced by pytest)
- **Line Length**: 100 characters (black and isort)
- **Import Style**: Black profile with trailing commas
- **Test Discovery**: Files matching `test_*.py` in `tests/` directory
