# Product Overview

Connections is a Python CLI tool that generates interactive flight connection maps by visualizing flight routes between airports on a world map.

## Core Functionality

- Accepts JSON input containing flight data with IATA airport codes
- Automatically looks up airport coordinates using the airports-py library
- Generates high-resolution PNG visualizations using Plotly
- Creates interactive maps with airport markers and flight route lines
- Supports global airport coverage via IATA codes

## Use Cases

- Personal travel history visualization
- Airline route network mapping
- Regional flight connection analysis
- Geographic flight data presentation

## Input Format

JSON array of flight objects with `src_iata` and `dst_iata` fields (3-letter IATA codes).

## Output

High-resolution PNG images (1920x1080 default) with geographic projections, airport markers, and connecting flight lines.
