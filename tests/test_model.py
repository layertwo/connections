from unittest.mock import MagicMock, patch

import geojson
import pytest

from connections.model import Coordinates, Flight, convert_airport_to_coords


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear lru_cache before each test to prevent cross-test contamination"""
    convert_airport_to_coords.cache_clear()
    yield
    convert_airport_to_coords.cache_clear()


class TestCoordinates:
    def test_coordinates_creation(self):
        """Test Coordinates dataclass creation"""
        coords = Coordinates(latitude=40.6413, longitude=-73.7781)
        assert coords.latitude == 40.6413
        assert coords.longitude == -73.7781


class TestConvertAirportToCoords:
    def test_convert_airport_to_coords_integration(self):
        """Test airport IATA to coordinates conversion with real data"""
        coords = convert_airport_to_coords("JFK")

        assert isinstance(coords, Coordinates)
        # Just check that we get reasonable coordinates for JFK (NYC area)
        assert 40.0 < coords.latitude < 41.0
        assert -74.0 < coords.longitude < -73.0

    def test_convert_airport_to_coords_caching_integration(self):
        """Test that airport conversion is cached with real data"""
        # Call twice with same IATA code
        coords1 = convert_airport_to_coords("LAX")
        coords2 = convert_airport_to_coords("LAX")

        # Should return same object due to caching
        assert coords1 == coords2
        # Just check that we get reasonable coordinates for LAX (LA area)
        assert 33.0 < coords1.latitude < 34.0
        assert -119.0 < coords1.longitude < -118.0


class TestFlight:
    def test_flight_creation(self):
        """Test Flight creation"""
        flight = Flight(src_iata="LAX", dst_iata="JFK")
        assert flight.src_iata == "LAX"
        assert flight.dst_iata == "JFK"

    def test_from_dict(self):
        """Test Flight.from_dict class method"""
        data = {"src_iata": "LAX", "dst_iata": "JFK"}
        flight = Flight.from_dict(data)

        assert isinstance(flight, Flight)
        assert flight.src_iata == "LAX"
        assert flight.dst_iata == "JFK"

    @patch("connections.model.convert_airport_to_coords")
    def test_coordinate_properties(self, mock_convert):
        """Test flight coordinate properties"""
        # Mock coordinate conversion
        mock_convert.side_effect = [
            Coordinates(latitude=33.9425, longitude=-118.4081),  # LAX
            Coordinates(latitude=40.6413, longitude=-73.7781),  # JFK
        ]

        flight = Flight(src_iata="LAX", dst_iata="JFK")

        # Test source coordinates
        assert flight.src_lat == 33.9425
        assert flight.src_lon == -118.4081

        # Test destination coordinates
        assert flight.dst_lat == 40.6413
        assert flight.dst_lon == -73.7781

    @patch("connections.model.convert_airport_to_coords")
    def test_coordinate_caching(self, mock_convert):
        """Test that coordinate properties are cached"""
        mock_convert.side_effect = [
            Coordinates(latitude=33.9425, longitude=-118.4081),  # LAX
            Coordinates(latitude=40.6413, longitude=-73.7781),  # JFK
        ]

        flight = Flight(src_iata="LAX", dst_iata="JFK")

        # Access coordinates multiple times
        _ = flight.src_coords
        _ = flight.src_coords
        _ = flight.dst_coords
        _ = flight.dst_coords

        # Should only call convert function twice (once for each airport)
        assert mock_convert.call_count == 2

    @patch("connections.model.convert_airport_to_coords")
    def test_as_feature(self, mock_convert):
        """Test GeoJSON feature generation"""
        mock_convert.side_effect = [
            Coordinates(latitude=33.9425, longitude=-118.4081),  # LAX
            Coordinates(latitude=40.6413, longitude=-73.7781),  # JFK
        ]

        flight = Flight(src_iata="LAX", dst_iata="JFK")
        feature = flight.as_feature()

        assert isinstance(feature, geojson.Feature)
        assert isinstance(feature.geometry, geojson.LineString)

        # Check coordinates in GeoJSON format (note: GeoJSON uses [lat, lon] format)
        expected_coords = [
            [33.9425, -118.4081],  # LAX - lists not tuples
            [40.6413, -73.7781],  # JFK
        ]
        assert feature.geometry.coordinates == expected_coords

    def test_get_coords_static_method(self):
        """Test that _get_coords calls convert_airport_to_coords"""
        with patch("connections.model.convert_airport_to_coords") as mock_convert:
            mock_convert.return_value = Coordinates(latitude=40.6413, longitude=-73.7781)

            coords = Flight._get_coords("JFK")

            assert isinstance(coords, Coordinates)
            mock_convert.assert_called_once_with("JFK")

    def test_flight_equality(self):
        """Test Flight equality comparison"""
        flight1 = Flight(src_iata="LAX", dst_iata="JFK")
        flight2 = Flight(src_iata="LAX", dst_iata="JFK")
        flight3 = Flight(src_iata="JFK", dst_iata="LAX")

        assert flight1 == flight2
        assert flight1 != flight3
