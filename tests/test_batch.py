import json
from pathlib import Path

import pytest

from connections.batch import BatchProcessor


class TestBatchProcessor:
    def test_process_all_generates_maps_for_all_json_files(self, tmp_path, mocker):
        """Test that batch processor generates a map for each JSON file"""
        # Arrange: Create input directory with JSON files
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        output_dir = tmp_path / "output"

        # Create sample JSON files
        flight_data = [
            {"src_iata": "JFK", "dst_iata": "LAX"},
            {"src_iata": "LAX", "dst_iata": "SFO"},
        ]

        (input_dir / "trip1.json").write_text(json.dumps(flight_data))
        (input_dir / "trip2.json").write_text(json.dumps(flight_data))

        # Mock airport lookups
        mock_airport = mocker.patch("connections.model.airport_data.get_airport_by_iata")
        mock_airport.return_value = [{"latitude": "40.6413", "longitude": "-73.7781"}]

        # Mock FlightMap.save to avoid actual file I/O
        mock_save = mocker.patch("connections.map.FlightMap.save")

        # Act
        processor = BatchProcessor(str(input_dir), str(output_dir))
        generated_files = processor.process_all()

        # Assert
        assert len(generated_files) == 2
        assert str(output_dir / "trip1.png") in generated_files
        assert str(output_dir / "trip2.png") in generated_files
        assert mock_save.call_count == 2

    def test_process_all_creates_output_directory(self, tmp_path, mocker):
        """Test that output directory is created if it doesn't exist"""
        # Arrange
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        output_dir = tmp_path / "output"

        flight_data = [{"src_iata": "JFK", "dst_iata": "LAX"}]
        (input_dir / "trip1.json").write_text(json.dumps(flight_data))

        mock_airport = mocker.patch("connections.model.airport_data.get_airport_by_iata")
        mock_airport.return_value = [{"latitude": "40.6413", "longitude": "-73.7781"}]
        mocker.patch("connections.map.FlightMap.save")

        # Act
        processor = BatchProcessor(str(input_dir), str(output_dir))
        processor.process_all()

        # Assert
        assert output_dir.exists()

    def test_process_all_uses_filename_as_title(self, tmp_path, mocker):
        """Test that filename (without extension) is used as map title"""
        # Arrange
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        output_dir = tmp_path / "output"

        flight_data = [{"src_iata": "JFK", "dst_iata": "LAX"}]
        (input_dir / "my_trip.json").write_text(json.dumps(flight_data))

        mock_airport = mocker.patch("connections.model.airport_data.get_airport_by_iata")
        mock_airport.return_value = [{"latitude": "40.6413", "longitude": "-73.7781"}]

        # Mock FlightMap to capture title
        mock_flight_map = mocker.patch("connections.batch.FlightMap")

        # Act
        processor = BatchProcessor(str(input_dir), str(output_dir))
        processor.process_all()

        # Assert
        mock_flight_map.assert_called_once()
        call_kwargs = mock_flight_map.call_args[1]
        assert call_kwargs["title"] == "my_trip"

    def test_process_all_skips_invalid_json_files(self, tmp_path, mocker):
        """Test that invalid JSON files are skipped with warning"""
        # Arrange
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        output_dir = tmp_path / "output"

        # Create one valid and one invalid JSON file
        valid_data = [{"src_iata": "JFK", "dst_iata": "LAX"}]
        (input_dir / "valid.json").write_text(json.dumps(valid_data))
        (input_dir / "invalid.json").write_text("not valid json")

        mock_airport = mocker.patch("connections.model.airport_data.get_airport_by_iata")
        mock_airport.return_value = [{"latitude": "40.6413", "longitude": "-73.7781"}]
        mocker.patch("connections.map.FlightMap.save")

        # Act
        processor = BatchProcessor(str(input_dir), str(output_dir))
        generated_files = processor.process_all()

        # Assert: Only valid file should be processed
        assert len(generated_files) == 1
        assert str(output_dir / "valid.png") in generated_files

    def test_process_all_returns_empty_list_when_no_json_files(self, tmp_path):
        """Test that empty list is returned when no JSON files found"""
        # Arrange
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        output_dir = tmp_path / "output"

        # Act
        processor = BatchProcessor(str(input_dir), str(output_dir))
        generated_files = processor.process_all()

        # Assert
        assert generated_files == []

    def test_process_all_raises_error_for_nonexistent_input_dir(self, tmp_path):
        """Test that error is raised if input directory doesn't exist"""
        # Arrange
        input_dir = tmp_path / "nonexistent"
        output_dir = tmp_path / "output"

        # Act & Assert
        processor = BatchProcessor(str(input_dir), str(output_dir))
        with pytest.raises(ValueError, match="Input directory does not exist"):
            processor.process_all()

    def test_process_single_generates_correct_output_path(self, tmp_path, mocker):
        """Test that _process_single generates correct output path"""
        # Arrange
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        flight_data = [{"src_iata": "JFK", "dst_iata": "LAX"}]
        json_path = input_dir / "test_flight.json"
        json_path.write_text(json.dumps(flight_data))

        mock_airport = mocker.patch("connections.model.airport_data.get_airport_by_iata")
        mock_airport.return_value = [{"latitude": "40.6413", "longitude": "-73.7781"}]
        mocker.patch("connections.map.FlightMap.save")

        # Act
        processor = BatchProcessor(str(input_dir), str(output_dir))
        output_path = processor._process_single(json_path)

        # Assert
        assert output_path == str(output_dir / "test_flight.png")
