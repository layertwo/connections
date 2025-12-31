import json
import logging
from pathlib import Path
from typing import List

from connections.map import FlightMap
from connections.model import Flight, Flights
from connections.utils import ensure_directory_exists

logger = logging.getLogger(__name__)


class BatchProcessor:
    """Processes multiple flight JSON files and generates maps"""

    def __init__(self, input_dir: str, output_dir: str):
        """
        Initialize batch processor

        Args:
            input_dir: Directory containing JSON files
            output_dir: Directory where PNG files will be saved
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)

    def process_all(self) -> List[str]:
        """
        Process all JSON files in input directory and generate flight maps

        Returns:
            List of generated file paths

        Raises:
            ValueError: If input directory doesn't exist
        """
        if not self.input_dir.exists():
            raise ValueError(f"Input directory does not exist: {self.input_dir}")

        # Create output directory if it doesn't exist
        ensure_directory_exists(self.output_dir)

        # Find all JSON files
        json_files = list(self.input_dir.glob("*.json"))

        if not json_files:
            logger.warning(f"No JSON files found in {self.input_dir}")
            return []

        generated_files = []
        for json_path in json_files:
            try:
                output_path = self._process_single(json_path)
                generated_files.append(output_path)
            except Exception as e:
                logger.warning(f"Failed to process {json_path.name}: {type(e).__name__}: {str(e)}")
                continue

        return generated_files

    def _process_single(self, json_path: Path) -> str:
        """
        Process a single JSON file and generate flight map

        Args:
            json_path: Path to JSON file

        Returns:
            Path to generated PNG file

        Raises:
            json.JSONDecodeError: If file is not valid JSON
            KeyError: If JSON doesn't contain required fields
            Exception: For other processing errors
        """
        # Read and parse JSON
        with open(json_path) as fp:
            data = json.load(fp)

        # Create Flight objects
        flights: Flights = [Flight.from_dict(d) for d in data]

        # Use filename (without extension) as title
        title = json_path.stem

        # Generate output filename
        output_filename = f"{title}.png"
        output_path = self.output_dir / output_filename

        # Create and save map
        fm = FlightMap(flights=flights, title=title)
        fm.save(filename=str(output_path))

        return str(output_path)
