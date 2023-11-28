from enum import Enum
from functools import lru_cache

import plotly.graph_objects as go
from pyairports.airports import Airports

from connections.model import Flights


@lru_cache()
def convert_airport_to_coords(iata: str):
    """Get airport lat/lon from iata code"""
    airport_client = Airports()
    airport = airport_client.lookup(iata)
    return airport.lat, airport.lon


class ImageFormat(Enum):
    PNG = "png"


class FlightMap:
    def __init__(self, flights: Flights, image_format: ImageFormat = ImageFormat.PNG) -> None:
        self._flights = flights
        self._image_format = image_format

    def draw(self) -> go.Figure:
        """Generate map from flights and airports"""
        fig = go.Figure(
            layout=dict(
                # title_text="2022",
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
                    # add source IATA point
                    go.Scattergeo(
                        lon=[flight.src_lon],
                        lat=[flight.src_lat],
                        hoverinfo="text",
                        text=flight.src_iata,
                        mode="markers",
                        marker=dict(
                            size=15,
                            line=dict(width=3),
                        ),
                    ),
                    # add dest IATA point
                    go.Scattergeo(
                        lon=[flight.dst_lon],
                        lat=[flight.dst_lat],
                        hoverinfo="text",
                        text=flight.dst_iata,
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
                        line=dict(width=2),  # color="orange"),
                    ),
                ]
            )

        return fig

    @property
    def fig(self) -> go.Figure:
        return self.draw()

    @lru_cache()
    def to_image(self, width: int = 1920, height: int = 1080):
        return self.fig.to_image(format=self._image_format.value, width=width, height=height, scale=10)

    def save(self, filename: str) -> None:
        image = self.to_image()
        with open(f"{filename}.{self._image_format.value}", "wb") as fp:
            fp.write(image)
