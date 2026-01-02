from enum import Enum
from functools import lru_cache
from typing import Dict, Set, Tuple

import plotly.graph_objects as go

from connections.model import Flights, MetroArea, consolidate_metro_areas


class ImageFormat(Enum):
    PNG = "png"


class FlightMap:
    def __init__(
        self, flights: Flights, title: str, image_format: ImageFormat = ImageFormat.PNG
    ) -> None:
        self._flights = flights
        self._title = title
        self._image_format = image_format
        # Consolidate metro areas on initialization
        self._metro_areas, self._trip_counts = consolidate_metro_areas(flights)

    def _calculate_marker_size(self, trip_count: int, min_size: int = 5, max_size: int = 25) -> int:
        """Calculate marker size based on trip count"""
        if trip_count == 0:
            return min_size
        # Use logarithmic scaling for better visual distribution
        import math

        # Get unique metros by name
        seen_names = set()
        unique_metros = []
        for metro in self._metro_areas.values():
            if metro.name not in seen_names:
                seen_names.add(metro.name)
                unique_metros.append(metro)

        max_trips = max((metro.trip_count for metro in unique_metros), default=0)
        if max_trips == 0:
            return min_size

        # Logarithmic scale
        normalized = math.log(trip_count + 1) / math.log(max_trips + 1)
        return int(min_size + (max_size - min_size) * normalized)

    def draw(self, thumbnail: bool = False) -> go.Figure:
        """Generate map from flights and airports

        Args:
            thumbnail: If True, optimize layout for thumbnail display
        """
        # Adjust layout for thumbnail vs full-size
        if thumbnail:
            title_config = None
            margin_config = dict(l=0, r=0, t=0, b=0)
        else:
            title_config = go.layout.Title(
                text=self._title,
                font=dict(family="Arial", size=50),
                xanchor="center",
                yanchor="top",
                x=0.5,
            )
            margin_config = dict(l=0, r=0, t=80, b=0)

        fig = go.Figure(
            layout=dict(
                title=title_config,
                showlegend=False,
                autosize=True,
                margin=margin_config,
                paper_bgcolor="rgba(0,0,0,0)",
                geo=dict(
                    fitbounds="locations",
                    showframe=False,
                    projection=dict(
                        type="natural earth1",
                    ),
                    bgcolor="rgba(0,0,0,0)",
                    showland=True,
                    showsubunits=True,
                    showcountries=True,
                ),
            )
        )

        # Get unique metro areas by name
        seen_names = set()
        unique_metros = []
        for metro in self._metro_areas.values():
            if metro.name not in seen_names:
                seen_names.add(metro.name)
                unique_metros.append(metro)

        # Add metro area markers
        for metro in unique_metros:
            marker_size = self._calculate_marker_size(metro.trip_count)
            fig.add_trace(
                go.Scattergeo(
                    lon=[metro.center.longitude],
                    lat=[metro.center.latitude],
                    hoverinfo="text",
                    text=f"{metro.name}<br>Trips: {metro.trip_count}",
                    mode="markers",
                    marker=dict(
                        size=marker_size,
                        line=dict(width=2),
                    ),
                )
            )

        # Add flight lines between metro areas
        for (src_name, dst_name), count in self._trip_counts.items():
            # Find the metro areas by name
            src_metro = next(m for m in unique_metros if m.name == src_name)
            dst_metro = next(m for m in unique_metros if m.name == dst_name)

            fig.add_trace(
                go.Scattergeo(
                    lon=[src_metro.center.longitude, dst_metro.center.longitude],
                    lat=[src_metro.center.latitude, dst_metro.center.latitude],
                    mode="lines",
                    line=dict(width=1 + count * 0.5),  # Line width scales with trip count
                    hoverinfo="text",
                    text=f"{src_name} → {dst_name}<br>Trips: {count}",
                )
            )

        return fig

    @property
    def fig(self) -> go.Figure:
        return self.draw()

    @lru_cache()
    def to_image(self, width: int = 1920, height: int = 1080):
        return self.fig.to_image(
            format=self._image_format.value, width=width, height=height, scale=10
        )

    def to_thumbnail(self, width: int = 640, height: int = 360) -> bytes:
        """Generate thumbnail image at lower resolution with optimized layout"""
        thumbnail_fig = self.draw(thumbnail=True)
        return thumbnail_fig.to_image(
            format=self._image_format.value, width=width, height=height, scale=5
        )

    def save(self, filename: str) -> None:
        image = self.to_image()
        with open(filename, "wb") as fp:
            fp.write(image)

    def save_with_thumbnail(self, filename: str) -> str:
        """
        Save both full-size image and thumbnail

        Args:
            filename: Path for the full-size image

        Returns:
            Path to the generated thumbnail file
        """
        # Save full-size image
        self.save(filename)

        # Generate thumbnail filename
        from pathlib import Path

        path = Path(filename)
        thumbnail_path = path.parent / f"{path.stem}_thumb{path.suffix}"

        # Save thumbnail
        thumbnail_image = self.to_thumbnail()
        with open(thumbnail_path, "wb") as fp:
            fp.write(thumbnail_image)

        return str(thumbnail_path)
