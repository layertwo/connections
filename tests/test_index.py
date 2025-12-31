from pathlib import Path

import pytest

from connections.index import IndexGenerator, MapMetadata


class TestMapMetadata:
    def test_map_metadata_creation(self):
        """Test MapMetadata dataclass creation"""
        metadata = MapMetadata(title="Test Map", filename="test.png", relative_path="./test.png")

        assert metadata.title == "Test Map"
        assert metadata.filename == "test.png"
        assert metadata.relative_path == "./test.png"
        assert metadata.thumbnail_path is None

    def test_map_metadata_with_thumbnail(self):
        """Test MapMetadata with thumbnail path"""
        metadata = MapMetadata(
            title="Test Map",
            filename="test.png",
            relative_path="./test.png",
            thumbnail_path="./test_thumb.png",
        )

        assert metadata.title == "Test Map"
        assert metadata.filename == "test.png"
        assert metadata.relative_path == "./test.png"
        assert metadata.thumbnail_path == "./test_thumb.png"


class TestIndexGenerator:
    def test_scan_output_directory_with_png_files(self, tmp_path):
        """Test scanning directory with PNG files"""
        # Create test PNG files
        (tmp_path / "map1.png").touch()
        (tmp_path / "map2.png").touch()
        (tmp_path / "map3.png").touch()

        generator = IndexGenerator()
        metadata_list = generator.scan_output_directory(str(tmp_path))

        assert len(metadata_list) == 3
        assert metadata_list[0].title == "map1"
        assert metadata_list[0].filename == "map1.png"
        assert metadata_list[0].relative_path == "./map1.png"
        assert metadata_list[1].title == "map2"
        assert metadata_list[2].title == "map3"

    def test_scan_output_directory_empty(self, tmp_path):
        """Test scanning empty directory"""
        generator = IndexGenerator()
        metadata_list = generator.scan_output_directory(str(tmp_path))

        assert metadata_list == []

    def test_scan_output_directory_nonexistent(self, tmp_path):
        """Test scanning non-existent directory"""
        nonexistent = tmp_path / "nonexistent"
        generator = IndexGenerator()
        metadata_list = generator.scan_output_directory(str(nonexistent))

        assert metadata_list == []

    def test_scan_output_directory_ignores_non_png(self, tmp_path):
        """Test that scanning ignores non-PNG files"""
        (tmp_path / "map1.png").touch()
        (tmp_path / "data.json").touch()
        (tmp_path / "readme.txt").touch()

        generator = IndexGenerator()
        metadata_list = generator.scan_output_directory(str(tmp_path))

        assert len(metadata_list) == 1
        assert metadata_list[0].filename == "map1.png"

    def test_generate_index_html(self, tmp_path):
        """Test generating index.html file"""
        maps = [
            MapMetadata(title="Trip 1", filename="trip1.png", relative_path="./trip1.png"),
            MapMetadata(title="Trip 2", filename="trip2.png", relative_path="./trip2.png"),
        ]

        output_path = tmp_path / "index.html"
        generator = IndexGenerator()
        generator.generate(maps, str(output_path))

        assert output_path.exists()

        # Verify content
        content = output_path.read_text()
        assert "Trip 1" in content
        assert "Trip 2" in content
        assert "trip1.png" in content
        assert "trip2.png" in content
        assert "./trip1.png" in content
        assert "./trip2.png" in content

    def test_generate_index_html_empty_maps(self, tmp_path):
        """Test generating index.html with no maps"""
        maps = []

        output_path = tmp_path / "index.html"
        generator = IndexGenerator()
        generator.generate(maps, str(output_path))

        assert output_path.exists()

        content = output_path.read_text()
        assert "No flight maps found" in content

    def test_generate_creates_parent_directories(self, tmp_path):
        """Test that generate creates parent directories if they don't exist"""
        maps = [MapMetadata(title="Test", filename="test.png", relative_path="./test.png")]

        output_path = tmp_path / "nested" / "dir" / "index.html"
        generator = IndexGenerator()
        generator.generate(maps, str(output_path))

        assert output_path.exists()
        assert output_path.parent.exists()

    def test_scan_output_directory_with_thumbnails(self, tmp_path):
        """Test scanning directory with PNG files and their thumbnails"""
        # Create test PNG files and thumbnails
        (tmp_path / "map1.png").touch()
        (tmp_path / "map1_thumb.png").touch()
        (tmp_path / "map2.png").touch()
        (tmp_path / "map2_thumb.png").touch()
        (tmp_path / "map3.png").touch()

        generator = IndexGenerator()
        metadata_list = generator.scan_output_directory(str(tmp_path))

        # Should only return 3 maps (not 6 - thumbnails are excluded)
        assert len(metadata_list) == 3

        # Check that thumbnails are properly linked
        assert metadata_list[0].title == "map1"
        assert metadata_list[0].thumbnail_path == "./map1_thumb.png"

        assert metadata_list[1].title == "map2"
        assert metadata_list[1].thumbnail_path == "./map2_thumb.png"

        assert metadata_list[2].title == "map3"
        assert metadata_list[2].thumbnail_path is None  # No thumbnail for map3

    def test_scan_output_directory_ignores_thumbnail_files(self, tmp_path):
        """Test that thumbnail files are not treated as separate maps"""
        (tmp_path / "map1.png").touch()
        (tmp_path / "map1_thumb.png").touch()
        (tmp_path / "standalone_thumb.png").touch()

        generator = IndexGenerator()
        metadata_list = generator.scan_output_directory(str(tmp_path))

        # Should only return map1, not the thumbnail files
        assert len(metadata_list) == 1
        assert metadata_list[0].title == "map1"

    def test_generate_index_html_with_thumbnails(self, tmp_path):
        """Test generating index.html with thumbnail paths"""
        maps = [
            MapMetadata(
                title="Trip 1",
                filename="trip1.png",
                relative_path="./trip1.png",
                thumbnail_path="./trip1_thumb.png",
            ),
            MapMetadata(
                title="Trip 2",
                filename="trip2.png",
                relative_path="./trip2.png",
                thumbnail_path="./trip2_thumb.png",
            ),
        ]

        output_path = tmp_path / "index.html"
        generator = IndexGenerator()
        generator.generate(maps, str(output_path))

        assert output_path.exists()

        # Verify content includes thumbnails
        content = output_path.read_text()
        assert "trip1_thumb.png" in content
        assert "trip2_thumb.png" in content
        # Full images should still be in href links
        assert 'href="./trip1.png"' in content
        assert 'href="./trip2.png"' in content
