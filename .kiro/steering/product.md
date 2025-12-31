---
inclusion: always
---

# Product Overview

Connections is a Python CLI tool that generates flight connection map visualizations from airport route data. It converts IATA airport codes to geographic coordinates and renders them as PNG images using Plotly.

## Core Functionality

**Command**: `poetry run connections -i INPUT_FILE -o OUTPUT_FILE -t TITLE`

**Input Format** (JSON array):
```json
[
  {"src_iata": "JFK", "dst_iata": "LHR"},
  {"src_iata": "LAX", "dst_iata": "NRT"}
]
```

**Output**: PNG image (1920x1080) showing flight routes on a world map with Natural Earth projection

## Critical Product Rules

### Input/Output Constraints
- **IATA codes**: Must be valid 3-letter codes (e.g., JFK, LHR, NRT)
- **JSON structure**: Array of objects with `src_iata` and `dst_iata` fields (exact field names required)
- **Output format**: PNG only (no SVG, PDF, or interactive HTML)
- **Resolution**: Fixed at 1920x1080 pixels
- **Coordinate source**: airports-py library (external dependency, must be mocked in tests)

### Error Handling Requirements
- **Invalid IATA codes**: Raise descriptive exceptions immediately (fail fast)
- **Missing airports**: Clear error message indicating which code failed
- **File I/O errors**: Propagate with context (e.g., "Cannot read input file: path/to/file.json")
- **No silent failures**: All errors must be visible to the user

### Performance Requirements
- **Coordinate lookups**: Must be cached using `@lru_cache()` to avoid repeated API calls
- **Image generation**: Must be cached using `@cached_property` or `@lru_cache()`
- **Rationale**: airports-py lookups and Plotly rendering are expensive operations

## Visual Output Specifications

### Map Rendering
- Each flight = line connecting source and destination coordinates
- Airport markers at all coordinate locations
- Natural Earth projection for global route visualization
- Title displayed prominently (user-configurable via `-t` flag)

### When Modifying Visualizations
- Maintain geographic accuracy (don't distort projections)
- Ensure routes are clearly visible against map background
- Keep consistent styling across all generated maps
- Test with sample data from `flights/` directory

## User Experience Principles

### Simplicity
- Single command execution (no interactive prompts or multi-step workflows)
- Three required flags: `-i` (input), `-o` (output), `-t` (title)
- No configuration files or environment setup beyond Poetry

### Reliability
- Validate all IATA codes before rendering
- Fail fast with clear error messages
- Never produce partial or corrupted output

### Clarity
- Visual output should immediately convey route connections
- Error messages should guide users to fix issues (e.g., "Invalid IATA code 'XYZ' in flight 3")

## AI Assistant Guidelines

### When Adding Features
- Preserve single-command simplicity (no new interactive modes)
- Maintain PNG-only output constraint
- Keep coordinate lookups cached
- Add tests for new functionality

### When Fixing Bugs
- Verify fix with sample data from `flights/` directory
- Ensure error messages remain clear and actionable
- Run full test suite to prevent regressions

### When Refactoring
- Never remove caching decorators without performance justification
- Maintain JSON input format compatibility
- Keep CLI interface stable (flags: `-i`, `-o`, `-t`)

## Sample Data Location

Test your changes with real-world data in `flights/` directory:
- `flights/north-america.json` - Regional routes
- `flights/transatlantic.json` - Long-haul routes
- `flights/world-tour.json` - Global coverage
