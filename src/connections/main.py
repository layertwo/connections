import json
import logging
from pathlib import Path

import click

from connections.batch import BatchProcessor
from connections.index import IndexGenerator
from connections.map import FlightMap
from connections.model import Flight, Flights

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


@click.group()
def cli() -> None:
    """Connections - Flight map visualization tool"""
    pass


@cli.command()
@click.option("-i", "--input-filename", type=click.Path(exists=True), required=True)
@click.option("-o", "--output-filename", type=str, required=True)
@click.option("-t", "--title", type=str, required=True)
def render(input_filename: str, output_filename: str, title: str) -> None:
    """Generate a single flight map from a JSON file"""
    with open(input_filename) as fp:
        data = json.loads(fp.read())
    flights: Flights = [Flight.from_dict(d) for d in data]
    fm = FlightMap(flights=flights, title=title)
    fm.save(filename=output_filename)


@cli.command()
@click.option("-d", "--input-directory", type=click.Path(exists=True), required=True)
@click.option("-o", "--output-directory", type=str, required=True)
def batch(input_directory: str, output_directory: str) -> None:
    """Generate flight maps for all JSON files in a directory"""
    processor = BatchProcessor(input_dir=input_directory, output_dir=output_directory)
    generated_files = processor.process_all()

    if generated_files:
        click.echo(f"Successfully generated {len(generated_files)} flight map(s):")
        for file_path in generated_files:
            click.echo(f"  - {file_path}")
    else:
        click.echo("No flight maps were generated.")


@cli.command()
@click.option("-d", "--directory", type=click.Path(exists=True), required=True)
@click.option("-o", "--output", type=str, default=None)
def index(directory: str, output: str) -> None:
    """Generate index.html from PNG files in a directory"""
    generator = IndexGenerator()
    maps = generator.scan_output_directory(directory)

    if not maps:
        click.echo("No PNG files found in directory.")
        return

    # Default output path is index.html in the same directory
    if output is None:
        output = str(Path(directory) / "index.html")

    generator.generate(maps=maps, output_path=output)
    click.echo(f"Generated index page at {output}")
    click.echo(f"Found {len(maps)} flight map(s)")


if __name__ == "__main__":
    cli()
