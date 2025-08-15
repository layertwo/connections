# connections

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)

A Python tool that creates interactive flight connection maps by visualizing flight routes between airports on a world map. Transform JSON flight data into beautiful geographic visualizations using Plotly.

## Features

- 🗺️ **Interactive Maps**: Generate high-quality flight route visualizations
- ✈️ **Airport Support**: Automatic airport coordinate lookup using IATA codes
- 🎨 **Customizable**: Add custom titles and styling to your maps
- 📊 **Multiple Formats**: Export maps as PNG images
- 🌍 **Global Coverage**: Support for airports worldwide via IATA codes
- 📋 **Simple Input**: JSON-based flight data format

## Installation

### Using Poetry (Recommended)

```bash
git clone https://github.com/layertwo/connections.git
cd connections
poetry install
```

### Requirements

- Python 3.10 or higher
- Poetry (for dependency management)

## Quick Start

1. **Prepare your flight data** in JSON format:
```json
[
  {
    "src_iata": "LAX",
    "dst_iata": "JFK"
  },
  {
    "src_iata": "LHR", 
    "dst_iata": "CDG"
  }
]
```

2. **Generate a flight map**:
```bash
poetry run connections -i sample_flights.json -o my_flight_map.png -t "My Flight Connections"
```

3. **View your generated map**: The command creates a PNG image file showing your flight routes on a world map.

## Usage

### Command Line Interface

```bash
connections -i INPUT_FILE -o OUTPUT_FILE -t TITLE
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `-i, --input-filename` | Yes | Path to JSON file containing flight data |
| `-o, --output-filename` | Yes | Output filename for the generated map image |
| `-t, --title` | Yes | Title to display on the map |

### Examples

**Basic usage with sample data:**
```bash
poetry run connections -i sample_flights.json -o world_flights.png -t "Global Flight Network"
```

**Custom flight data:**
```bash
poetry run connections -i my_flights.json -o vacation_routes.png -t "My Travel History"
```

## Input Data Format

The input JSON file should contain an array of flight objects. Each flight requires:

- `src_iata`: Source airport IATA code (3-letter code, e.g., "LAX")
- `dst_iata`: Destination airport IATA code (3-letter code, e.g., "JFK")

### Example Input File

```json
[
  {
    "src_iata": "LAX",
    "dst_iata": "JFK"
  },
  {
    "src_iata": "LHR",
    "dst_iata": "CDG"
  },
  {
    "src_iata": "NRT",
    "dst_iata": "ICN"
  },
  {
    "src_iata": "DXB",
    "dst_iata": "SIN"
  }
]
```

### Supported Airport Codes

The tool uses the `airports-py` library, which supports thousands of airports worldwide. Ensure your IATA codes are valid 3-letter airport identifiers (e.g., LAX, JFK, LHR).

## Output

The tool generates:

- **High-resolution PNG images** (1920x1080 by default)
- **Interactive maps** with airport markers and flight route lines
- **Geographic projection** using Natural Earth projection for optimal global visualization
- **Hover information** showing flight route details (src → dst)

### Map Features

- Airport locations marked with circular markers
- Flight routes shown as connecting lines
- Custom title positioning and styling
- Automatic map bounds fitting to include all flight routes
- Country and continent boundaries for geographic context

## Development

### Setup Development Environment

```bash
git clone https://github.com/layertwo/connections.git
cd connections
poetry install --with dev
```

### Running Tests

```bash
# Run all tests with coverage
poetry run pytest

# Run tests with coverage report
poetry run pytest --cov=src/connections --cov-report=html
```

### Code Formatting

```bash
# Format code with black
poetry run black src/ tests/

# Sort imports with isort
poetry run isort src/ tests/
```

### Project Structure

```
connections/
├── src/connections/
│   ├── __init__.py
│   ├── main.py      # CLI interface and main entry point
│   ├── model.py     # Flight and coordinate data models
│   └── map.py       # Map generation and visualization
├── tests/           # Test suite
├── sample_flights.json  # Example flight data
└── pyproject.toml   # Project configuration
```

## Dependencies

- **plotly**: Interactive map visualization and chart generation
- **airports-py**: Airport data and coordinate lookup by IATA code
- **geojson**: Geographic data format handling
- **click**: Command-line interface framework
- **kaleido**: Static image export for Plotly charts

## Examples

### Personal Travel Map
Create a map of your personal travel history:
```bash
poetry run connections -i my_travels.json -o my_travel_map.png -t "My Travel Journey"
```

### Airline Route Network
Visualize an airline's route network:
```bash
poetry run connections -i airline_routes.json -o route_network.png -t "Airline Route Network"
```

### Regional Connections
Map regional flight connections:
```bash
poetry run connections -i europe_flights.json -o europe_map.png -t "European Flight Connections"
```

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`poetry run pytest`)
5. Format code (`poetry run black src/ tests/ && poetry run isort src/ tests/`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request
