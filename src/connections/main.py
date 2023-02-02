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


def draw_map(df_airports: pd.DataFrame, df_flight_paths: pd.DataFrame):
    """Generate map from flights and airports"""
    fig = go.Figure()

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

    fig.update_layout(
        title_text="2022",
        showlegend=False,
        geo=dict(
            scope="north america",
            projection_type="azimuthal equal area",
            showland=True,
            landcolor="rgb(243, 243, 243)",
            countrycolor="rgb(204, 204, 204)",
        ),
    )

    fig.show()


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

    draw_map(df_airports, df_flight_paths)

    filename = "map.png"


if __name__ == "__main__":
    main()
