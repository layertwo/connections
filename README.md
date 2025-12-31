# connections

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)

A Python tool that creates interactive flight connection maps by visualizing flight routes between airports on a world map. Transform JSON flight data into beautiful geographic visualizations using Plotly.

## Features

- 🗺️ **Interactive Maps**: Generate high-quality flight route visualizations
- ✈️ **Airport Support**: Automatic airport coordinate lookup using IATA codes
- 🎨 **Customizable**: Add custom titles and styling to your maps
- 📊 **Multiple Formats**: Export maps as PNG images
- 🌍 **Global Coverage**: Support for airports worldwide via IATA codes
- 📋 **Simple Input**: JSON-based flight data format

## Installation

### Using Poetry (Recommended)

```bash
git clone https://github.com/layertwo/connections.git
cd connections
poetry install
```

### Requirements

- Python 3.10 or higher
- Poetry (for dependency management)

## Quick Start

1. **Prepare your flight data** in JSON format:
```json
[
  {
    "src_iata": "LAX",
    "dst_iata": "JFK"
  },
  {
    "src_iata": "LHR", 
    "dst_iata": "CDG"
  }
]
```

2. **Generate a flight map**:
```bash
poetry run connections -i sample_flights.json -o my_flight_map.png -t "My Flight Connections"
```

3. **View your generated map**: The command creates a PNG image file showing your flight routes on a world map.

## Usage

### Command Line Interface

The tool provides three commands:

#### 1. Single Map Generation (`render`)

```bash
connections render -i INPUT_FILE -o OUTPUT_FILE -t TITLE
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `-i, --input-filename` | Yes | Path to JSON file containing flight data |
| `-o, --output-filename` | Yes | Output filename for the generated map image |
| `-t, --title` | Yes | Title to display on the map |

**Example:**
```bash
poetry run connections render -i sample_flights.json -o world_flights.png -t "Global Flight Network"
```

#### 2. Batch Map Generation (`batch`)

Generate multiple flight maps from a directory of JSON files:

```bash
connections batch -d INPUT_DIRECTORY -o OUTPUT_DIRECTORY
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `-d, --input-directory` | Yes | Directory containing JSON flight data files |
| `-o, --output-directory` | Yes | Directory where generated maps will be saved |

**Example:**
```bash
poetry run connections batch -d flights/ -o output/
```

The batch command will:
- Process all `.json` files in the input directory
- Use the filename (without extension) as the map title
- Generate PNG files with corresponding names in the output directory
- Skip invalid files and log warnings

#### 3. Index Page Generation (`index`)

Generate an HTML index page listing all flight maps:

```bash
connections index -d DIRECTORY -o OUTPUT_FILE
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `-d, --directory` | Yes | Directory containing PNG flight maps |
| `-o, --output` | No | Output path for index.html (defaults to DIRECTORY/index.html) |

**Example:**
```bash
poetry run connections index -d output/ -o output/index.html
```

## Input Data Format

The input JSON file should contain an array of flight objects. Each flight requires:

- `src_iata`: Source airport IATA code (3-letter code, e.g., "LAX")
- `dst_iata`: Destination airport IATA code (3-letter code, e.g., "JFK")

### Example Input File

```json
[
  {
    "src_iata": "LAX",
    "dst_iata": "JFK"
  },
  {
    "src_iata": "LHR",
    "dst_iata": "CDG"
  },
  {
    "src_iata": "NRT",
    "dst_iata": "ICN"
  },
  {
    "src_iata": "DXB",
    "dst_iata": "SIN"
  }
]
```

### Supported Airport Codes

The tool uses the `airports-py` library, which supports thousands of airports worldwide. Ensure your IATA codes are valid 3-letter airport identifiers (e.g., LAX, JFK, LHR).

## Output

The tool generates:

- **High-resolution PNG images** (1920x1080 by default)
- **Interactive maps** with airport markers and flight route lines
- **Geographic projection** using Natural Earth projection for optimal global visualization
- **Hover information** showing flight route details (src → dst)

### Map Features

- Airport locations marked with circular markers
- Flight routes shown as connecting lines
- Custom title positioning and styling
- Automatic map bounds fitting to include all flight routes
- Country and continent boundaries for geographic context

## Development

### Setup Development Environment

```bash
git clone https://github.com/layertwo/connections.git
cd connections
poetry install --with dev
```

### Running Tests

```bash
# Run all tests with coverage
poetry run pytest

# Run tests with coverage report
poetry run pytest --cov=src/connections --cov-report=html
```

### Code Formatting

```bash
# Format code with black
poetry run black src/ tests/

# Sort imports with isort
poetry run isort src/ tests/
```

### Project Structure

```
connections/
├── .github/workflows/
│   └── deploy.yml   # Automated deployment workflow
├── flights/         # Flight data directory (for automated deployment)
├── src/connections/
│   ├── __init__.py
│   ├── main.py      # CLI interface with render, batch, and index commands
│   ├── model.py     # Flight and coordinate data models
│   ├── map.py       # Map generation and visualization
│   ├── batch.py     # Batch processing for multiple files
│   ├── index.py     # HTML index page generation
│   └── templates/
│       └── index.html.j2  # Jinja2 template for index page
├── cdk/             # AWS CDK infrastructure code
│   ├── bin/
│   │   ├── github-oidc-app.ts  # OIDC infrastructure app
│   ├── lib/
│   │   ├── app.ts          # Main CDK application entry point
│   │   ├── connections.ts  # S3 and CloudFront stack
│   │   └── github-oidc.ts  # GitHub OIDC provider and IAM role stack
│   └── package.json
├── tests/           # Test suite
├── sample_flights.json  # Example flight data
└── pyproject.toml   # Project configuration
```

## Dependencies

### Production Dependencies
- **plotly**: Interactive map visualization and chart generation
- **airports-py**: Airport data and coordinate lookup by IATA code
- **geojson**: Geographic data format handling
- **click**: Command-line interface framework
- **kaleido**: Static image export for Plotly charts
- **jinja2**: HTML template engine for index page generation

### Development Dependencies
- **pytest**: Testing framework
- **pytest-mock**: Mocking support for tests
- **pytest-cov**: Code coverage reporting
- **black**: Code formatter
- **isort**: Import sorter

### Infrastructure Dependencies
- **AWS CDK**: Infrastructure as code for S3 and CloudFront deployment
- **Node.js**: Required for CDK deployment

## Examples

### Single Map Generation

**Personal Travel Map:**
```bash
poetry run connections render -i my_travels.json -o my_travel_map.png -t "My Travel Journey"
```

**Airline Route Network:**
```bash
poetry run connections render -i airline_routes.json -o route_network.png -t "Airline Route Network"
```

### Batch Processing

**Process Multiple Trip Files:**
```bash
# Create a directory with multiple JSON files
mkdir flights
# Add trip1.json, trip2.json, etc.
poetry run connections batch -d flights/ -o output/
```

**Generate Index Page:**
```bash
poetry run connections index -d output/
# Opens output/index.html in browser to view all maps
```

## Automated Deployment

### GitHub Actions Workflow

The project includes a GitHub Actions workflow that automatically:
1. Generates flight maps from JSON files in the `flights/` directory
2. Creates an HTML index page
3. Deploys everything to AWS S3 via CDK

### Setup for Automated Deployment

This project uses OpenID Connect (OIDC) to allow GitHub Actions to securely access AWS without storing long-term credentials. The setup is automated using CDK.

#### Step 1: Bootstrap CDK in Your AWS Account

First, bootstrap CDK to create the necessary IAM roles and resources:

```bash
cd cdk
npx cdk bootstrap aws://YOUR-ACCOUNT-ID/us-east-1
```

This creates essential roles with tags like `aws-cdk:bootstrap-role` that are used for deployment.

#### Step 2: Deploy GitHub OIDC Infrastructure

Deploy the OIDC provider and IAM role using the provided CDK stack:

```bash
cd cdk
npm install
npm run build

# Set your GitHub organization and repository
export GITHUB_ORG="your-github-org"
export GITHUB_REPO="your-repo-name"

# Optional: Restrict to specific branch (recommended for production)
export GITHUB_BRANCH="main"

# Deploy the OIDC stack
npm run deploy:oidc
```

This will create:
- GitHub OIDC identity provider in AWS
- IAM role that GitHub Actions can assume
- Permissions to assume CDK bootstrap roles

After deployment, the stack outputs the role ARN - save this for the next step.

#### Step 3: Configure GitHub Secrets

Add this secret to your GitHub repository (Settings → Secrets and variables → Actions):

| Secret | Description | Example |
|--------|-------------|---------|
| `AWS_ROLE_ARN` | ARN from the OIDC stack output | `arn:aws:iam::123456789012:role/GitHubActionsDeployRole` |

#### Step 4: Create Flight Data and Deploy

1. **Create a `flights/` directory** in your repository with JSON flight data files

2. **Push changes to main branch:**
   ```bash
   mkdir flights
   # Add your JSON files to flights/
   git add flights/
   git commit -m "Add flight data"
   git push origin main
   ```

3. **View your deployed site** at the CloudFront URL output by the CDK deployment

### Required GitHub Secrets

| Secret | Description |
|--------|-------------|
| `AWS_ROLE_ARN` | ARN of the IAM role for OIDC authentication (from OIDC stack output) |

### Security Benefits of OIDC

Using OIDC instead of long-term access keys provides:
- **No stored credentials**: No AWS access keys in GitHub secrets
- **Temporary credentials**: GitHub requests short-lived tokens from AWS
- **Fine-grained access**: Restrict which repositories/branches can deploy
- **Audit trail**: All role assumptions logged in CloudTrail

For more information, see: [GitHub Docs - Configuring OpenID Connect in AWS](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws)

### Workflow Triggers

The deployment workflow runs when:
- Changes are pushed to `main` branch in the `flights/` directory
- Changes are made to source code or CDK infrastructure
- Manually triggered via workflow_dispatch

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`poetry run pytest`)
5. Format code (`poetry run black src/ tests/ && poetry run isort src/ tests/`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request
