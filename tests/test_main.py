import json
from unittest.mock import MagicMock, mock_open, patch

import pytest
from click.testing import CliRunner

from connections.main import render
from connections.model import Flight


class TestRenderCommand:
    @pytest.fixture
    def runner(self):
        """Create Click CLI test runner"""
        return CliRunner()

    @pytest.fixture
    def mock_flight_map(self):
        """Mock FlightMap for testing"""
        with patch("connections.main.FlightMap") as mock_fm:
            mock_instance = MagicMock()
            mock_fm.return_value = mock_instance
            yield mock_instance

    def test_render_command_success(self, runner, sample_flight_json_file, mock_flight_map):
        """Test successful execution of render command"""
        output_file = "test_output.png"
        title = "Test Flight Map"

        with patch("connections.main.Flight.from_dict") as mock_from_dict:
            mock_flight = MagicMock(spec=Flight)
            mock_from_dict.return_value = mock_flight

            result = runner.invoke(
                render,
                [
                    "--input-filename",
                    sample_flight_json_file,
                    "--output-filename",
                    output_file,
                    "--title",
                    title,
                ],
            )

            assert result.exit_code == 0
            mock_flight_map.save.assert_called_once_with(filename=output_file)

    def test_render_command_missing_input_file(self, runner):
        """Test render command with missing input file"""
        result = runner.invoke(
            render,
            [
                "--input-filename",
                "nonexistent.json",
                "--output-filename",
                "output.png",
                "--title",
                "Test",
            ],
        )

        assert result.exit_code != 0
        assert "does not exist" in result.output

    def test_render_command_missing_required_options(self, runner):
        """Test render command with missing required options"""
        # Missing all options
        result = runner.invoke(render, [])
        assert result.exit_code != 0

        # Missing output filename
        result = runner.invoke(render, ["--input-filename", "test.json"])
        assert result.exit_code != 0

        # Missing title
        result = runner.invoke(
            render, ["--input-filename", "test.json", "--output-filename", "output.png"]
        )
        assert result.exit_code != 0

    def test_render_command_json_parsing(self, runner, mock_flight_map):
        """Test JSON file parsing in render command"""
        test_data = [{"src_iata": "LAX", "dst_iata": "JFK"}]

        with runner.isolated_filesystem():
            with open("test.json", "w") as f:
                json.dump(test_data, f)

            with patch("connections.main.Flight.from_dict") as mock_from_dict:
                mock_flight = MagicMock(spec=Flight)
                mock_from_dict.return_value = mock_flight

                result = runner.invoke(
                    render,
                    [
                        "--input-filename",
                        "test.json",
                        "--output-filename",
                        "output.png",
                        "--title",
                        "Test Map",
                    ],
                )

                assert result.exit_code == 0
                mock_from_dict.assert_called_once_with({"src_iata": "LAX", "dst_iata": "JFK"})

    def test_render_command_invalid_json(self, runner):
        """Test render command with invalid JSON"""
        with runner.isolated_filesystem():
            with open("invalid.json", "w") as f:
                f.write("invalid json")

            result = runner.invoke(
                render,
                [
                    "--input-filename",
                    "invalid.json",
                    "--output-filename",
                    "output.png",
                    "--title",
                    "Test Map",
                ],
            )

            assert result.exit_code != 0

    def test_render_command_creates_flight_objects(
        self, runner, sample_flight_json_file, mock_flight_map
    ):
        """Test that render command creates Flight objects from JSON data"""
        with patch("connections.main.Flight.from_dict") as mock_from_dict:
            mock_flight = MagicMock(spec=Flight)
            mock_from_dict.return_value = mock_flight

            result = runner.invoke(
                render,
                [
                    "--input-filename",
                    sample_flight_json_file,
                    "--output-filename",
                    "output.png",
                    "--title",
                    "Test Map",
                ],
            )

            assert result.exit_code == 0
            # Should call from_dict for each flight in the sample data
            assert mock_from_dict.call_count == 3  # 3 flights in sample_flight_data fixture

    def test_render_command_passes_correct_parameters_to_flight_map(
        self, runner, sample_flight_json_file
    ):
        """Test that render command passes correct parameters to FlightMap"""
        title = "My Flight Map"

        with patch("connections.main.FlightMap") as mock_fm_class:
            mock_fm_instance = MagicMock()
            mock_fm_class.return_value = mock_fm_instance

            with patch("connections.main.Flight.from_dict") as mock_from_dict:
                mock_flight = MagicMock(spec=Flight)
                mock_from_dict.return_value = mock_flight

                result = runner.invoke(
                    render,
                    [
                        "--input-filename",
                        sample_flight_json_file,
                        "--output-filename",
                        "output.png",
                        "--title",
                        title,
                    ],
                )

                assert result.exit_code == 0

                # Check FlightMap was called with correct parameters
                mock_fm_class.assert_called_once()
                call_args = mock_fm_class.call_args
                assert call_args[1]["title"] == title
                assert "flights" in call_args[1]

    def test_render_command_short_options(self, runner, sample_flight_json_file, mock_flight_map):
        """Test render command with short option flags"""
        with patch("connections.main.Flight.from_dict") as mock_from_dict:
            mock_flight = MagicMock(spec=Flight)
            mock_from_dict.return_value = mock_flight

            result = runner.invoke(
                render,
                ["-i", sample_flight_json_file, "-o", "output.png", "-t", "Test Map"],
            )

            assert result.exit_code == 0
            mock_flight_map.save.assert_called_once_with(filename="output.png")

    def test_render_command_empty_json_array(self, runner, mock_flight_map):
        """Test render command with empty JSON array"""
        with runner.isolated_filesystem():
            # Create empty JSON file
            with open("empty.json", "w") as f:
                json.dump([], f)

            result = runner.invoke(
                render,
                [
                    "--input-filename",
                    "empty.json",
                    "--output-filename",
                    "output.png",
                    "--title",
                    "Empty Map",
                ],
            )

            assert result.exit_code == 0
            mock_flight_map.save.assert_called_once_with(filename="output.png")

    def test_render_command_file_operations(self, runner, mock_flight_map):
        """Test file operations in render command"""
        test_data = [{"src_iata": "LAX", "dst_iata": "JFK"}]

        with runner.isolated_filesystem():
            with open("test.json", "w") as f:
                json.dump(test_data, f)

            with patch("connections.main.Flight.from_dict") as mock_from_dict:
                mock_flight = MagicMock(spec=Flight)
                mock_from_dict.return_value = mock_flight

                result = runner.invoke(
                    render,
                    [
                        "--input-filename",
                        "test.json",
                        "--output-filename",
                        "output.png",
                        "--title",
                        "Test Map",
                    ],
                )

                assert result.exit_code == 0
                mock_from_dict.assert_called_once_with({"src_iata": "LAX", "dst_iata": "JFK"})

    def test_render_command_help(self, runner):
        """Test render command help output"""
        result = runner.invoke(render, ["--help"])

        assert result.exit_code == 0
        assert "--input-filename" in result.output
        assert "--output-filename" in result.output
        assert "--title" in result.output
        assert "-i" in result.output
        assert "-o" in result.output
        assert "-t" in result.output

    def test_render_command_integration_with_real_json(self, runner, mock_flight_map):
        """Test render command with realistic JSON structure"""
        test_data = [
            {"src_iata": "LAX", "dst_iata": "JFK"},
            {"src_iata": "LHR", "dst_iata": "CDG"},
            {"src_iata": "NRT", "dst_iata": "ICN"},
        ]

        with runner.isolated_filesystem():
            with open("flights.json", "w") as f:
                json.dump(test_data, f)

            with patch("connections.main.Flight.from_dict") as mock_from_dict:
                mock_flight = MagicMock(spec=Flight)
                mock_from_dict.return_value = mock_flight

                result = runner.invoke(
                    render,
                    [
                        "--input-filename",
                        "flights.json",
                        "--output-filename",
                        "map.png",
                        "--title",
                        "Global Flights",
                    ],
                )

                assert result.exit_code == 0
                assert mock_from_dict.call_count == 3
                mock_flight_map.save.assert_called_once_with(filename="map.png")
