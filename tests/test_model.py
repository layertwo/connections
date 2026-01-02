from unittest.mock import MagicMock, patch

import geojson
import pytest

from connections.model import (
    Coordinates,
    Flight,
    MetroArea,
    consolidate_metro_areas,
    convert_airport_to_coords,
)


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


class TestCoordinatesDistance:
    def test_distance_to_same_point(self):
        """Test distance between same coordinates is zero"""
        coords = Coordinates(latitude=40.6413, longitude=-73.7781)
        distance = coords.distance_to(coords)
        assert distance == 0.0

    def test_distance_to_different_points(self):
        """Test distance calculation between JFK and LAX"""
        jfk = Coordinates(latitude=40.6413, longitude=-73.7781)
        lax = Coordinates(latitude=33.9425, longitude=-118.4081)
        distance = jfk.distance_to(lax)
        # JFK to LAX is approximately 2475 miles
        assert 2400 < distance < 2550

    def test_distance_is_symmetric(self):
        """Test that distance(A, B) == distance(B, A)"""
        coords1 = Coordinates(latitude=40.6413, longitude=-73.7781)
        coords2 = Coordinates(latitude=33.9425, longitude=-118.4081)
        assert coords1.distance_to(coords2) == coords2.distance_to(coords1)


class TestMetroArea:
    @patch("connections.model.convert_airport_to_coords")
    def test_from_airport(self, mock_convert):
        """Test creating metro area from single airport"""
        mock_convert.return_value = Coordinates(latitude=40.6413, longitude=-73.7781)

        metro = MetroArea.from_airport("JFK")

        assert metro.name == "JFK"
        assert metro.iata_codes == {"JFK"}
        assert metro.center.latitude == 40.6413
        assert metro.center.longitude == -73.7781
        assert metro.trip_count == 0

    @patch("connections.model.convert_airport_to_coords")
    def test_add_airport(self, mock_convert):
        """Test adding airport to metro area"""
        # Need enough mock returns for initial creation and recalculation
        mock_convert.side_effect = [
            Coordinates(latitude=40.6413, longitude=-73.7781),  # JFK initial
            Coordinates(latitude=40.6413, longitude=-73.7781),  # JFK for recalc
            Coordinates(latitude=40.7769, longitude=-73.8740),  # LGA for recalc
        ]

        metro = MetroArea.from_airport("JFK")
        metro.add_airport("LGA", Coordinates(latitude=40.7769, longitude=-73.8740))

        assert "LGA" in metro.iata_codes
        assert "JFK" in metro.iata_codes
        assert metro.name == "JFK/LGA"
        # Center should be average of both airports
        assert 40.7 < metro.center.latitude < 40.8
        assert -73.9 < metro.center.longitude < -73.7

    def test_contains(self):
        """Test metro area contains method"""
        metro = MetroArea(
            name="NYC",
            iata_codes={"JFK", "LGA", "EWR"},
            center=Coordinates(latitude=40.7, longitude=-73.9),
        )

        assert metro.contains("JFK")
        assert metro.contains("LGA")
        assert metro.contains("EWR")
        assert not metro.contains("LAX")


class TestConsolidateMetroAreas:
    @patch("connections.model.convert_airport_to_coords")
    def test_consolidate_nearby_airports(self, mock_convert):
        """Test that nearby airports are consolidated into metro areas"""
        # JFK and LGA are about 8 miles apart
        # Use a dict to return consistent coordinates for each airport
        coords_map = {
            "JFK": Coordinates(latitude=40.6413, longitude=-73.7781),
            "LGA": Coordinates(latitude=40.7769, longitude=-73.8740),
            "LAX": Coordinates(latitude=33.9425, longitude=-118.4081),
        }
        mock_convert.side_effect = lambda iata: coords_map[iata]

        flights = [
            Flight(src_iata="JFK", dst_iata="LAX"),
            Flight(src_iata="LGA", dst_iata="LAX"),
        ]

        metro_areas, trip_counts = consolidate_metro_areas(flights, distance_threshold=50.0)

        # JFK and LGA should be in same metro area
        assert metro_areas["JFK"] is metro_areas["LGA"]
        assert metro_areas["JFK"].name == "JFK/LGA"

        # LAX should be separate
        assert metro_areas["LAX"].name == "LAX"

    @patch("connections.model.convert_airport_to_coords")
    def test_consolidate_trip_counts(self, mock_convert):
        """Test that trip counts are calculated correctly"""
        mock_convert.side_effect = [
            Coordinates(latitude=47.4502, longitude=-122.3088),  # SEA
            Coordinates(latitude=44.8848, longitude=-93.2223),  # MSP
            Coordinates(latitude=47.4502, longitude=-122.3088),  # SEA
            Coordinates(latitude=44.8848, longitude=-93.2223),  # MSP
        ]

        flights = [
            Flight(src_iata="SEA", dst_iata="MSP"),
            Flight(src_iata="SEA", dst_iata="MSP"),
            Flight(src_iata="MSP", dst_iata="SEA"),
        ]

        metro_areas, trip_counts = consolidate_metro_areas(flights)

        # Check trip counts between metros
        assert trip_counts[("SEA", "MSP")] == 2
        assert trip_counts[("MSP", "SEA")] == 1

        # Check individual metro trip counts
        assert metro_areas["SEA"].trip_count == 3
        assert metro_areas["MSP"].trip_count == 3

    @patch("connections.model.convert_airport_to_coords")
    def test_consolidate_skips_intra_metro_flights(self, mock_convert):
        """Test that flights within same metro area are not counted"""
        # JFK and LGA are close enough to consolidate
        # Use a dict to return consistent coordinates for each airport
        coords_map = {
            "JFK": Coordinates(latitude=40.6413, longitude=-73.7781),
            "LGA": Coordinates(latitude=40.7769, longitude=-73.8740),
        }
        mock_convert.side_effect = lambda iata: coords_map[iata]

        flights = [
            Flight(src_iata="JFK", dst_iata="LGA"),
        ]

        metro_areas, trip_counts = consolidate_metro_areas(flights, distance_threshold=50.0)

        # Should have no inter-metro trips
        assert len(trip_counts) == 0

    @patch("connections.model.convert_airport_to_coords")
    def test_consolidate_distant_airports_separate(self, mock_convert):
        """Test that distant airports remain separate"""
        mock_convert.side_effect = [
            Coordinates(latitude=40.6413, longitude=-73.7781),  # JFK
            Coordinates(latitude=33.9425, longitude=-118.4081),  # LAX
        ]

        flights = [
            Flight(src_iata="JFK", dst_iata="LAX"),
        ]

        metro_areas, trip_counts = consolidate_metro_areas(flights, distance_threshold=50.0)

        # JFK and LAX should be separate metros
        assert metro_areas["JFK"] is not metro_areas["LAX"]
        assert metro_areas["JFK"].name == "JFK"
        assert metro_areas["LAX"].name == "LAX"
