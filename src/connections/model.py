from dataclasses import dataclass
from functools import cached_property, lru_cache
from typing import List

import geojson
from airports import airport_data


@dataclass
class Coordinates:
    latitude: float
    longitude: float


@lru_cache()
def convert_airport_to_coords(iata: str) -> Coordinates:
    """Get airport lat/lon from iata code"""
    airport = airport_data.get_airport_by_iata(iata)[0]
    return Coordinates(latitude=float(airport["latitude"]), longitude=float(airport["longitude"]))


@dataclass
class Flight:
    src_iata: str
    dst_iata: str

    @classmethod
    def from_dict(cls, data: dict) -> "Flight":
        """Create Flight instance from dictionary"""
        return cls(
            src_iata=data["src_iata"],
            dst_iata=data["dst_iata"]
        )

    @property
    def src_lat(self) -> float:
        return self.src_coords.latitude

    @property
    def src_lon(self) -> float:
        return self.src_coords.longitude

    @property
    def dst_lat(self) -> float:
        return self.dst_coords.latitude

    @property
    def dst_lon(self) -> float:
        return self.dst_coords.longitude

    @staticmethod
    def _get_coords(iata: str) -> Coordinates:
        return convert_airport_to_coords(iata)

    @cached_property
    def src_coords(self) -> Coordinates:
        return self._get_coords(iata=self.src_iata)

    @cached_property
    def dst_coords(self) -> Coordinates:
        return self._get_coords(iata=self.dst_iata)

    def as_feature(self) -> geojson.Feature:
        geometry = geojson.LineString(
            [
                (self.src_coords.latitude, self.src_coords.longitude),
                (self.dst_coords.latitude, self.dst_coords.longitude),
            ]
        )
        return geojson.Feature(geometry=geometry)


Flights = List[Flight]
