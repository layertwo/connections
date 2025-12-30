---
inclusion: always
---

# Product Overview

Connections is a Python CLI tool that generates flight connection map visualizations from airport route data.

## Purpose

Visualize flight routes between airports on a world map by converting IATA airport codes into geographic coordinates and rendering them as PNG images with Plotly.

## Key Constraints

- **Input**: JSON array with flight objects containing `src_iata` and `dst_iata` fields (3-letter IATA codes)
- **Output**: PNG images only (1920x1080 default resolution)
- **Coordinate Source**: airports-py library for IATA → lat/lon conversion
- **Projection**: Natural Earth projection for global visualization
- **Performance**: Coordinate lookups are cached to minimize API calls

## User Workflow

1. User provides JSON file with flight data via `-i` flag
2. Tool validates IATA codes and looks up coordinates
3. Tool generates Plotly figure with geo layout
4. Tool exports PNG to specified output path via `-o` flag
5. Optional custom title via `-t` flag

## Design Principles

- **Simplicity**: Single command execution, no interactive mode
- **Reliability**: Fail fast on invalid IATA codes or missing airports
- **Performance**: Cache coordinate lookups and image generation
- **Clarity**: Visual output should clearly show routes and airports

## Expected Behavior

- Each flight renders as a line connecting source and destination airports
- Airport markers appear at coordinate locations
- Map uses geographic projection suitable for global routes
- Invalid IATA codes should raise clear errors
- Missing input files should fail gracefully with helpful messages
