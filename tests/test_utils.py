"""Tests for utility functions"""

from pathlib import Path

import pytest

from connections.utils import ensure_directory_exists


class TestEnsureDirectoryExists:
    """Tests for ensure_directory_exists utility function"""

    def test_creates_directory_if_not_exists(self, tmp_path):
        """Test that directory is created when it doesn't exist"""
        new_dir = tmp_path / "test_dir"
        assert not new_dir.exists()

        result = ensure_directory_exists(new_dir)

        assert new_dir.exists()
        assert new_dir.is_dir()
        assert result == new_dir

    def test_creates_nested_directories(self, tmp_path):
        """Test that nested directories are created with parents=True"""
        nested_dir = tmp_path / "parent" / "child" / "grandchild"
        assert not nested_dir.exists()

        result = ensure_directory_exists(nested_dir)

        assert nested_dir.exists()
        assert nested_dir.is_dir()
        assert result == nested_dir

    def test_does_not_fail_if_directory_exists(self, tmp_path):
        """Test that function succeeds when directory already exists"""
        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()
        assert existing_dir.exists()

        result = ensure_directory_exists(existing_dir)

        assert existing_dir.exists()
        assert result == existing_dir

    def test_accepts_string_path(self, tmp_path):
        """Test that function accepts string paths"""
        new_dir = tmp_path / "string_dir"
        new_dir_str = str(new_dir)

        result = ensure_directory_exists(new_dir_str)

        assert new_dir.exists()
        assert new_dir.is_dir()
        assert result == new_dir

    def test_accepts_path_object(self, tmp_path):
        """Test that function accepts Path objects"""
        new_dir = tmp_path / "path_dir"

        result = ensure_directory_exists(new_dir)

        assert new_dir.exists()
        assert new_dir.is_dir()
        assert result == new_dir
