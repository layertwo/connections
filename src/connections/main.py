from functools import lru_cache

import pandas as pd
import plotly.graph_objects as go
from pyairports.airports import Airports


@lru_cache()
def convert_airport_to_coords(iata: str):
    """Get airport lat/lon from iata code"""
    airport_client = Airports()
    airport = airport_client.lookup(iata)
    return airport.lat, airport.lon


def draw_map(df_airports: pd.DataFrame, df_flight_paths: pd.DataFrame) -> go.Figure:
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
                landcolor="rgb(243, 243, 243)",
                countrycolor="rgb(204, 204, 204)",
            ),
        )
    )

    fig.add_trace(
        go.Scattergeo(
            locationmode="USA-states",
            lon=df_airports["lon"],
            lat=df_airports["lat"],
            hoverinfo="text",
            text=df_airports["iata"],
            mode="markers",
            marker=dict(size=10, color="orange", line=dict(width=3, color="orange")),
        )
    )

    for _, row in df_flight_paths.iterrows():
        fig.add_trace(
            go.Scattergeo(
                locationmode="USA-states",
                lon=[row["src_lon"], row["dst_lon"]],
                lat=[row["src_lat"], row["dst_lat"]],
                mode="lines",
                line=dict(width=1, color="orange"),
            )
        )

    return fig


def save_map(fig: go.Figure, filename: str) -> None:
    file_format = "png"
    image = fig.to_image(format=file_format, width=1920, height=1080, scale=10)
    with open(f"{filename}.{file_format}", "wb") as fp:
        fp.write(image)


def get_unique_airports(df: pd.DataFrame) -> pd.DataFrame:
    """Get unique airports and their lat/lon"""
    df_airports = pd.DataFrame({"iata": pd.concat([df["src_iata"], df["dst_iata"]]).unique()})
    df_airports[["lat", "lon"]] = (
        df_airports["iata"].apply(convert_airport_to_coords).apply(pd.Series)
    )
    return df_airports


def main():
    flight_filename = "flights.csv"
    df = pd.read_csv(flight_filename)
    df_airports = get_unique_airports(df)

    df_flight_paths = df.copy()
    df_flight_paths[["src_lat", "src_lon"]] = (
        df_flight_paths["src_iata"].apply(convert_airport_to_coords).apply(pd.Series)
    )
    df_flight_paths[["dst_lat", "dst_lon"]] = (
        df_flight_paths["dst_iata"].apply(convert_airport_to_coords).apply(pd.Series)
    )

    filename = "map"
    m = draw_map(df_airports, df_flight_paths)
    save_map(m, filename)


if __name__ == "__main__":
    main()
