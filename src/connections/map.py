from enum import Enum
from functools import lru_cache

import plotly.graph_objects as go
from pyairports.airports import Airports

from connections.model import Flights


class ImageFormat(Enum):
    PNG = "png"


class FlightMap:
    def __init__(
        self, flights: Flights, title: str, image_format: ImageFormat = ImageFormat.PNG
    ) -> None:
        self._flights = flights
        self._title = title
        self._image_format = image_format

    def draw(self) -> go.Figure:
        """Generate map from flights and airports"""
        fig = go.Figure(
            layout=dict(
                title=go.layout.Title(
                    text=self._title,
                    font=dict(family="Arial", size=50),
                    xanchor="center",
                    yanchor="top",
                    x=0.5,
                ),
                showlegend=False,
                autosize=True,
                geo=dict(
                    fitbounds="locations",
                    showframe=False,
                    projection=dict(
                        type="natural earth1",
                    ),
                    showland=True,
                    showsubunits=True,
                    showcountries=True,
                ),
            )
        )

        for flight in self._flights:
            fig.add_traces(
                [
                    # add IATA markers
                    go.Scattergeo(
                        lon=[flight.src_lon, flight.dst_lon],
                        lat=[flight.src_lat, flight.dst_lat],
                        hoverinfo="text",
                        text=f"{flight.src_iata} -> {flight.dst_iata}",
                        mode="markers",
                        marker=dict(
                            size=15,
                            line=dict(width=3),
                        ),
                    ),
                    # add flight line
                    go.Scattergeo(
                        lon=[flight.src_lon, flight.dst_lon],
                        lat=[flight.src_lat, flight.dst_lat],
                        mode="lines",
                        line=dict(width=2),
                    ),
                ]
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

    def save(self, filename: str) -> None:
        image = self.to_image()
        with open(filename, "wb") as fp:
            fp.write(image)
