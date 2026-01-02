from dataclasses import dataclass
from functools import cached_property, lru_cache
from math import asin, cos, radians, sin, sqrt
from typing import Dict, List, Set, Tuple

import geojson
from airports import airport_data


@dataclass
class Coordinates:
    latitude: float
    longitude: float

    def distance_to(self, other: "Coordinates") -> float:
        """Calculate distance in miles using haversine formula"""
        # Earth radius in miles
        R = 3959.0

        lat1, lon1 = radians(self.latitude), radians(self.longitude)
        lat2, lon2 = radians(other.latitude), radians(other.longitude)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))

        return R * c


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
        return cls(src_iata=data["src_iata"], dst_iata=data["dst_iata"])

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


@dataclass
class MetroArea:
    """Represents a consolidated metro area containing multiple nearby airports"""

    name: str
    iata_codes: Set[str]
    center: Coordinates
    trip_count: int = 0

    def __hash__(self):
        """Make MetroArea hashable based on name"""
        return hash(self.name)

    def __eq__(self, other):
        """Equality based on name"""
        if not isinstance(other, MetroArea):
            return False
        return self.name == other.name

    @classmethod
    def from_airport(cls, iata: str) -> "MetroArea":
        """Create a metro area from a single airport"""
        coords = convert_airport_to_coords(iata)
        return cls(name=iata, iata_codes={iata}, center=coords, trip_count=0)

    def add_airport(self, iata: str, coords: Coordinates) -> None:
        """Add an airport to this metro area and recalculate center"""
        if iata in self.iata_codes:
            return

        self.iata_codes.add(iata)
        # Update name to include all airports
        old_name = self.name
        self.name = "/".join(sorted(self.iata_codes))

        # Recalculate center as average of all airports
        all_coords = [convert_airport_to_coords(code) for code in self.iata_codes]
        self.center = Coordinates(
            latitude=sum(c.latitude for c in all_coords) / len(all_coords),
            longitude=sum(c.longitude for c in all_coords) / len(all_coords),
        )

    def contains(self, iata: str) -> bool:
        """Check if this metro area contains the given airport"""
        return iata in self.iata_codes


def consolidate_metro_areas(
    flights: Flights, distance_threshold: float = 50.0
) -> Tuple[Dict[str, MetroArea], Dict[Tuple[str, str], int]]:
    """
    Consolidate airports within distance_threshold miles into metro areas
    and count trips between metro areas.

    Args:
        flights: List of Flight objects
        distance_threshold: Maximum distance in miles to consolidate airports

    Returns:
        Tuple of (metro_areas_map, trip_counts)
        - metro_areas_map: Dict mapping IATA code to MetroArea
        - trip_counts: Dict mapping (src_metro, dst_metro) to trip count
    """
    # Build initial metro areas (one per unique airport)
    metro_areas: Dict[str, MetroArea] = {}
    all_airports: Set[str] = set()

    for flight in flights:
        all_airports.add(flight.src_iata)
        all_airports.add(flight.dst_iata)

    for iata in all_airports:
        metro_areas[iata] = MetroArea.from_airport(iata)

    # Consolidate nearby airports
    iata_list = sorted(all_airports)
    for i, iata1 in enumerate(iata_list):
        for iata2 in iata_list[i + 1 :]:
            metro1 = metro_areas[iata1]
            metro2 = metro_areas[iata2]

            # Skip if already in same metro
            if metro1 is metro2:
                continue

            # Check distance between metro centers
            distance = metro1.center.distance_to(metro2.center)

            if distance <= distance_threshold:
                # Merge metro2 into metro1
                for code in metro2.iata_codes:
                    metro1.add_airport(code, convert_airport_to_coords(code))
                    metro_areas[code] = metro1

    # Count trips between metro areas
    trip_counts: Dict[Tuple[str, str], int] = {}

    for flight in flights:
        src_metro = metro_areas[flight.src_iata]
        dst_metro = metro_areas[flight.dst_iata]

        # Skip intra-metro flights
        if src_metro is dst_metro:
            continue

        key = (src_metro.name, dst_metro.name)
        trip_counts[key] = trip_counts.get(key, 0) + 1

        # Also track individual metro trip counts
        src_metro.trip_count += 1
        dst_metro.trip_count += 1

    return metro_areas, trip_counts
