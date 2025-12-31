"""Utility functions for the connections package"""

from pathlib import Path


def ensure_directory_exists(directory: Path | str) -> Path:
    """
    Create directory if it doesn't exist

    Args:
        directory: Directory path (Path object or string)

    Returns:
        Path object for the created/existing directory

    Raises:
        OSError: If directory creation fails due to permissions or other OS errors
    """
    dir_path = Path(directory) if isinstance(directory, str) else directory
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path
