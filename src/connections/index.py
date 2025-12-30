import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from jinja2 import FileSystemLoader, PackageLoader
from jinja2.sandbox import SandboxedEnvironment

logger = logging.getLogger(__name__)


@dataclass
class MapMetadata:
    """Metadata for a flight map"""

    title: str
    filename: str
    relative_path: str


class IndexGenerator:
    """Generates HTML index page for flight maps"""

    def __init__(self, template_path: Optional[str] = None):
        """
        Initialize Jinja2 environment

        Args:
            template_path: Optional custom template directory path.
                          If None, uses default package templates.
        """
        if template_path:
            template_dir = Path(template_path)
            self.env = SandboxedEnvironment(loader=FileSystemLoader(template_dir))
        else:
            # Use package templates
            self.env = SandboxedEnvironment(loader=PackageLoader("connections", "templates"))

    def generate(self, maps: List[MapMetadata], output_path: str) -> None:
        """
        Generate HTML from template and map metadata, save to file

        Args:
            maps: List of map metadata objects
            output_path: Path where index.html will be saved
        """
        template = self.env.get_template("index.html.j2")
        html_content = template.render(maps=maps)

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as fp:
            fp.write(html_content)

        logger.info(f"Generated index page at {output_path}")

    def scan_output_directory(self, directory: str) -> List[MapMetadata]:
        """
        Scan directory for PNG files and extract metadata

        Args:
            directory: Directory path to scan for PNG files

        Returns:
            List of MapMetadata objects for each PNG file found
        """
        dir_path = Path(directory)

        if not dir_path.exists():
            logger.warning(f"Directory does not exist: {directory}")
            return []

        png_files = sorted(dir_path.glob("*.png"))

        if not png_files:
            logger.warning(f"No PNG files found in {directory}")
            return []

        metadata_list = []
        for png_file in png_files:
            # Use filename (without extension) as title
            title = png_file.stem
            filename = png_file.name
            # Relative path for HTML links
            relative_path = f"./{filename}"

            metadata = MapMetadata(title=title, filename=filename, relative_path=relative_path)
            metadata_list.append(metadata)

        return metadata_list
