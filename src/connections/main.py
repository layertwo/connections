import json

from connections.map import FlightMap
from connections.model import Flight, Flights


def main():
    filename = "configuration/flights-2022.json"
    with open(filename) as fp:
        data = json.loads(fp.read())
    flights: Flights = [Flight.from_dict(d) for d in data]
    fm = FlightMap(flights=flights)
    fm.save(filename="map")


if __name__ == "__main__":
    main()
