import json
from pathlib import Path

import pytest


@pytest.fixture
def sample_flight_data():
    """Sample flight data for testing"""
    return [
        {"src_iata": "LAX", "dst_iata": "JFK"},
        {"src_iata": "LHR", "dst_iata": "CDG"},
        {"src_iata": "NRT", "dst_iata": "ICN"},
    ]


@pytest.fixture
def sample_flight_json_file(tmp_path, sample_flight_data):
    """Create a temporary JSON file with sample flight data"""
    json_file = tmp_path / "test_flights.json"
    with open(json_file, "w") as f:
        json.dump(sample_flight_data, f)
    return str(json_file)


@pytest.fixture
def mock_airport_data():
    """Mock airport data for testing"""
    return {
        "LAX": [{"latitude": "33.9425", "longitude": "-118.4081"}],
        "JFK": [{"latitude": "40.6413", "longitude": "-73.7781"}],
        "LHR": [{"latitude": "51.4700", "longitude": "-0.4543"}],
        "CDG": [{"latitude": "49.0097", "longitude": "2.5479"}],
        "NRT": [{"latitude": "35.7647", "longitude": "140.3864"}],
        "ICN": [{"latitude": "37.4602", "longitude": "126.4407"}],
    }
