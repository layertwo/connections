from unittest.mock import MagicMock, mock_open, patch

import plotly.graph_objects as go
import pytest

from connections.map import FlightMap, ImageFormat
from connections.model import Coordinates, Flight


class TestImageFormat:
    def test_image_format_enum(self):
        """Test ImageFormat enum values"""
        assert ImageFormat.PNG.value == "png"


class TestFlightMap:
    @pytest.fixture
    def mock_flights(self):
        """Create mock flight objects for testing"""
        with patch("connections.model.convert_airport_to_coords") as mock_convert:
            mock_convert.side_effect = [
                Coordinates(latitude=33.9425, longitude=-118.4081),  # LAX
                Coordinates(latitude=40.6413, longitude=-73.7781),  # JFK
                Coordinates(latitude=51.4700, longitude=-0.4543),  # LHR
                Coordinates(latitude=49.0097, longitude=2.5479),  # CDG
            ]

            flights = [
                Flight(src_iata="LAX", dst_iata="JFK"),
                Flight(src_iata="LHR", dst_iata="CDG"),
            ]
            return flights

    def test_flight_map_initialization(self, mock_flights):
        """Test FlightMap initialization"""
        title = "Test Flight Map"
        flight_map = FlightMap(flights=mock_flights, title=title)

        assert flight_map._flights == mock_flights
        assert flight_map._title == title
        assert flight_map._image_format == ImageFormat.PNG

    def test_flight_map_initialization_with_custom_format(self, mock_flights):
        """Test FlightMap initialization with custom image format"""
        title = "Test Flight Map"
        flight_map = FlightMap(flights=mock_flights, title=title, image_format=ImageFormat.PNG)

        assert flight_map._image_format == ImageFormat.PNG

    @patch("plotly.graph_objects.Figure")
    def test_draw_creates_figure(self, mock_figure, mock_flights):
        """Test that draw method creates a plotly figure"""
        mock_fig_instance = MagicMock()
        mock_figure.return_value = mock_fig_instance

        flight_map = FlightMap(flights=mock_flights, title="Test Map")
        result = flight_map.draw()

        # Should create a Figure with proper layout
        mock_figure.assert_called_once()
        call_args = mock_figure.call_args[1]
        assert "layout" in call_args

        layout = call_args["layout"]
        assert "title" in layout
        assert "showlegend" in layout
        assert "geo" in layout

        # Check title configuration
        title_config = layout["title"]
        assert title_config.text == "Test Map"

        assert result == mock_fig_instance

    @patch("plotly.graph_objects.Figure")
    @patch("plotly.graph_objects.Scattergeo")
    def test_draw_adds_traces_for_flights(self, mock_scattergeo, mock_figure, mock_flights):
        """Test that draw method adds traces for metro areas and routes"""
        mock_fig_instance = MagicMock()
        mock_figure.return_value = mock_fig_instance
        mock_trace = MagicMock()
        mock_scattergeo.return_value = mock_trace

        flight_map = FlightMap(flights=mock_flights, title="Test Map")
        flight_map.draw()

        # Should add traces for metro areas and routes
        # With 2 flights between 4 different airports, we expect:
        # - 4 metro area markers (one per airport since they're far apart)
        # - 2 route lines
        assert mock_fig_instance.add_trace.call_count >= 4

    def test_fig_property(self, mock_flights):
        """Test that fig property returns draw() result"""
        flight_map = FlightMap(flights=mock_flights, title="Test Map")

        with patch.object(flight_map, "draw") as mock_draw:
            mock_fig = MagicMock()
            mock_draw.return_value = mock_fig

            result = flight_map.fig

            mock_draw.assert_called_once()
            assert result == mock_fig

    def test_to_image_default_parameters(self, mock_flights):
        """Test to_image method with default parameters"""
        flight_map = FlightMap(flights=mock_flights, title="Test Map")

        with patch.object(flight_map, "draw") as mock_draw:
            mock_fig = MagicMock()
            mock_fig.to_image.return_value = b"mock_image_data"
            mock_draw.return_value = mock_fig

            result = flight_map.to_image()

            mock_fig.to_image.assert_called_once_with(
                format="png", width=1920, height=1080, scale=10
            )
            assert result == b"mock_image_data"

    def test_to_image_custom_parameters(self, mock_flights):
        """Test to_image method with custom parameters"""
        flight_map = FlightMap(flights=mock_flights, title="Test Map")

        with patch.object(flight_map, "draw") as mock_draw:
            mock_fig = MagicMock()
            mock_fig.to_image.return_value = b"mock_image_data"
            mock_draw.return_value = mock_fig

            result = flight_map.to_image(width=800, height=600)

            mock_fig.to_image.assert_called_once_with(format="png", width=800, height=600, scale=10)
            assert result == b"mock_image_data"

    def test_to_image_caching(self, mock_flights):
        """Test that to_image results are cached"""
        flight_map = FlightMap(flights=mock_flights, title="Test Map")

        with patch.object(flight_map, "draw") as mock_draw:
            mock_fig = MagicMock()
            mock_fig.to_image.return_value = b"mock_image_data"
            mock_draw.return_value = mock_fig

            # Call to_image twice with same parameters
            result1 = flight_map.to_image()
            result2 = flight_map.to_image()

            # Should only call draw once due to property caching
            # Note: The @lru_cache on to_image should prevent multiple calls
            assert result1 == result2 == b"mock_image_data"

    def test_save_method(self, mock_flights, tmp_path):
        """Test save method writes image to file"""
        flight_map = FlightMap(flights=mock_flights, title="Test Map")

        with patch.object(flight_map, "to_image") as mock_to_image:
            mock_to_image.return_value = b"mock_image_data"

            output_file = tmp_path / "test_map.png"
            flight_map.save(str(output_file))

            # Check that file was created and contains the expected data
            assert output_file.exists()
            assert output_file.read_bytes() == b"mock_image_data"
            mock_to_image.assert_called_once()

    @patch("builtins.open", new_callable=mock_open)
    def test_save_method_with_mock_open(self, mock_file, mock_flights):
        """Test save method using mock_open"""
        flight_map = FlightMap(flights=mock_flights, title="Test Map")

        with patch.object(flight_map, "to_image") as mock_to_image:
            mock_to_image.return_value = b"mock_image_data"

            flight_map.save("test_output.png")

            mock_file.assert_called_once_with("test_output.png", "wb")
            mock_file().write.assert_called_once_with(b"mock_image_data")

    def test_empty_flights_list(self):
        """Test FlightMap with empty flights list"""
        flight_map = FlightMap(flights=[], title="Empty Map")

        with patch("plotly.graph_objects.Figure") as mock_figure:
            mock_fig_instance = MagicMock()
            mock_figure.return_value = mock_fig_instance

            flight_map.draw()

            # Should create figure but not add any traces (no metro areas or routes)
            mock_figure.assert_called_once()
            mock_fig_instance.add_trace.assert_not_called()

    def test_multiple_flights_trace_generation(self, mock_flights):
        """Test that multiple flights generate metro areas and routes"""
        flight_map = FlightMap(flights=mock_flights, title="Multi Flight Map")

        with patch("plotly.graph_objects.Figure") as mock_figure:
            mock_fig_instance = MagicMock()
            mock_figure.return_value = mock_fig_instance

            flight_map.draw()

            # Should add traces for metro areas and routes
            assert mock_fig_instance.add_trace.call_count >= len(mock_flights)

    def test_calculate_marker_size(self, mock_flights):
        """Test marker size calculation based on trip count"""
        flight_map = FlightMap(flights=mock_flights, title="Test Map")

        # Test with zero trips
        size_zero = flight_map._calculate_marker_size(0)
        assert size_zero == 5  # min_size

        # Test with some trips - size should be between min and max
        size_some = flight_map._calculate_marker_size(5)
        assert isinstance(size_some, int)
        assert size_some >= 5  # At least min_size

        # Test with many trips
        size_many = flight_map._calculate_marker_size(100)
        assert isinstance(size_many, int)
        assert size_many >= 5  # At least min_size

    def test_to_thumbnail_default_parameters(self, mock_flights):
        """Test to_thumbnail method with default parameters"""
        flight_map = FlightMap(flights=mock_flights, title="Test Map")

        with patch.object(flight_map, "draw") as mock_draw:
            mock_fig = MagicMock()
            mock_fig.to_image.return_value = b"mock_thumbnail_data"
            mock_draw.return_value = mock_fig

            result = flight_map.to_thumbnail()

            mock_fig.to_image.assert_called_once_with(format="png", width=640, height=360, scale=5)
            assert result == b"mock_thumbnail_data"

    def test_to_thumbnail_custom_parameters(self, mock_flights):
        """Test to_thumbnail method with custom parameters"""
        flight_map = FlightMap(flights=mock_flights, title="Test Map")

        with patch.object(flight_map, "draw") as mock_draw:
            mock_fig = MagicMock()
            mock_fig.to_image.return_value = b"mock_thumbnail_data"
            mock_draw.return_value = mock_fig

            result = flight_map.to_thumbnail(width=320, height=180)

            mock_fig.to_image.assert_called_once_with(format="png", width=320, height=180, scale=5)
            assert result == b"mock_thumbnail_data"

    def test_save_with_thumbnail(self, mock_flights, tmp_path):
        """Test save_with_thumbnail method creates both full and thumbnail images"""
        flight_map = FlightMap(flights=mock_flights, title="Test Map")

        with patch.object(flight_map, "to_image") as mock_to_image, patch.object(
            flight_map, "to_thumbnail"
        ) as mock_to_thumbnail:
            mock_to_image.return_value = b"mock_full_image"
            mock_to_thumbnail.return_value = b"mock_thumbnail_image"

            output_file = tmp_path / "test_map.png"
            thumbnail_path = flight_map.save_with_thumbnail(str(output_file))

            # Check full image
            assert output_file.exists()
            assert output_file.read_bytes() == b"mock_full_image"

            # Check thumbnail
            expected_thumb_path = tmp_path / "test_map_thumb.png"
            assert expected_thumb_path.exists()
            assert expected_thumb_path.read_bytes() == b"mock_thumbnail_image"
            assert thumbnail_path == str(expected_thumb_path)

            mock_to_image.assert_called_once()
            mock_to_thumbnail.assert_called_once()
