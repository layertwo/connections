import json

import click

from connections.map import FlightMap
from connections.model import Flight, Flights


@click.command()
@click.option("-i", "--input-filename", type=click.Path(exists=True), required=True)
@click.option("-o", "--output-filename", type=str, required=True)
@click.option("-t", "--title", type=str, required=True)
def render(input_filename: str, output_filename: str, title: str) -> None:
    with open(input_filename) as fp:
        data = json.loads(fp.read())
    flights: Flights = [Flight.from_dict(d) for d in data]
    fm = FlightMap(flights=flights, title=title)
    fm.save(filename=output_filename)


if __name__ == "__main__":
    main()
