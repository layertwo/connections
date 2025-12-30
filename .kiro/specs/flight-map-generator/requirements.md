# Requirements Document

## Introduction

This document specifies the requirements for the connections tool - a comprehensive flight map generator that creates visualizations of flight routes and enables sharing via AWS S3 static website hosting. The system generates flight connection maps from JSON data stored in a GitHub repository, and a GitHub Action automatically generates maps and uploads them to S3 whenever flight data is updated, making it easy to share flight visualizations with friends via a public URL.

## Glossary

- **System**: The connections CLI tool with AWS S3 upload capabilities
- **Flight Map**: A PNG image visualization of flight routes between airports
- **S3 Bucket**: An Amazon S3 bucket configured for static website hosting
- **Flight Data**: JSON array containing flight objects with source and destination IATA codes
- **GitHub Action**: An automated workflow that runs when flight data is committed to the repository
- **Workflow**: A GitHub Actions YAML file that defines the automation process
- **Static Website**: An S3 bucket configured to serve HTML and images via HTTP
- **Index Page**: An HTML page listing all uploaded Flight Maps with links and previews
- **AWS Credentials**: AWS access key ID and secret access key stored as GitHub secrets
- **CDK**: AWS Cloud Development Kit for defining infrastructure as TypeScript code
- **CloudFront**: AWS content delivery network for serving the static website globally
- **Route53**: AWS DNS service for managing custom domain names
- **Distribution**: A CloudFront distribution that caches and serves content from S3

## Requirements

### Requirement 1: Flight Map Generation

**User Story:** As a user, I want to generate flight maps from JSON data, so that I can visualize my flight connections.

#### Acceptance Criteria

1. WHEN a user provides Flight Data in JSON format, THE System SHALL parse it into Flight objects
2. WHEN Flight objects are created, THE System SHALL look up airport coordinates using IATA codes
3. WHEN generating a Flight Map, THE System SHALL create a PNG image with flight routes and airport markers
4. WHEN generating a Flight Map, THE System SHALL include a custom title on the map
5. THE System SHALL support saving Flight Maps to local files
6. THE System SHALL support generating Flight Maps in memory without saving to disk

### Requirement 2: Batch Map Generation

**User Story:** As a user, I want to generate multiple flight maps from multiple JSON files, so that I can process all my flight data at once.

#### Acceptance Criteria

1. WHEN a user provides a directory path, THE System SHALL find all JSON files in that directory
2. WHEN processing multiple files, THE System SHALL generate a separate Flight Map for each file
3. WHEN processing multiple files, THE System SHALL use the filename (without extension) as the default map title
4. WHEN generating multiple maps, THE System SHALL save them to a specified output directory
5. THE System SHALL skip files that cannot be parsed as valid Flight Data
6. THE System SHALL log warnings for skipped files with error details

### Requirement 3: GitHub Actions Workflow

**User Story:** As a user, I want a GitHub Action that automatically generates flight maps and uploads them to S3 when I commit flight data, so that I don't have to manually run commands.

#### Acceptance Criteria

1. WHEN flight data is pushed to the repository, THE Workflow SHALL trigger automatically
2. WHEN the Workflow runs, THE System SHALL install Python dependencies using Poetry
3. WHEN the Workflow runs, THE System SHALL generate Flight Maps from all JSON files in the flights directory
4. WHEN the Workflow runs, THE System SHALL upload generated Flight Maps to the configured S3 Bucket
5. WHEN the Workflow runs, THE System SHALL generate and upload an Index Page
6. WHEN the Workflow runs, THE System SHALL use AWS credentials from GitHub secrets
7. WHEN uploading to S3, THE System SHALL set content-type metadata appropriately
8. WHEN uploading to S3, THE System SHALL make uploaded files publicly accessible
9. IF the Workflow fails, THEN THE System SHALL provide error logs in the GitHub Actions output

### Requirement 4: Static Website Generation

**User Story:** As a user, I want an automatically generated HTML index page, so that I can view all my flight maps in one place and share a single URL with friends.

#### Acceptance Criteria

1. WHEN Flight Maps are uploaded to S3, THE System SHALL generate an Index Page listing all maps
2. WHEN generating the Index Page, THE System SHALL include thumbnail previews of each Flight Map
3. WHEN generating the Index Page, THE System SHALL include clickable links to full-resolution images
4. WHEN generating the Index Page, THE System SHALL include the title of each Flight Map
5. WHEN generating the Index Page, THE System SHALL upload it to the S3 Bucket as index.html
6. WHEN the Index Page is uploaded, THE System SHALL set content-type metadata to "text/html"
7. WHEN generating the Index Page, THE System SHALL display maps in reverse chronological order

### Requirement 5: AWS Infrastructure with CDK

**User Story:** As a user, I want to define my AWS infrastructure as code using TypeScript CDK, so that I can easily deploy and manage my S3 bucket, CloudFront distribution, and custom domain.

#### Acceptance Criteria

1. THE System SHALL include a CDK application written in TypeScript
2. WHEN the CDK application is deployed, THE System SHALL create an S3 Bucket for static website hosting
3. WHEN the CDK application is deployed, THE System SHALL create a CloudFront Distribution pointing to the S3 Bucket
4. WHEN the CDK application is deployed, THE System SHALL configure the CloudFront Distribution with appropriate caching policies
5. WHERE a custom domain is specified, THE System SHALL create Route53 DNS records pointing to the CloudFront Distribution
6. WHERE a custom domain is specified, THE System SHALL provision an ACM certificate for HTTPS
7. WHEN the CDK application is deployed, THE System SHALL configure the S3 Bucket policy to allow CloudFront access
8. WHEN the CDK application is deployed, THE System SHALL set index.html as the default root object
9. THE System SHALL output the CloudFront distribution URL after deployment
10. WHERE a custom domain is configured, THE System SHALL output the custom domain URL after deployment

### Requirement 6: CDK Stack Configuration

**User Story:** As a user, I want to configure my infrastructure settings, so that I can customize the bucket name, domain, and other AWS resources.

#### Acceptance Criteria

1. THE CDK application SHALL support configuration via environment variables
2. WHEN a BUCKET_NAME environment variable is provided, THE System SHALL use it for the S3 Bucket name
3. WHEN a DOMAIN_NAME environment variable is provided, THE System SHALL configure Route53 and ACM for that domain
4. WHEN a HOSTED_ZONE_ID environment variable is provided, THE System SHALL use the existing Route53 hosted zone
5. WHERE no custom domain is provided, THE System SHALL deploy without Route53 and ACM resources
6. THE CDK application SHALL use a single stack for all resources
7. THE CDK application SHALL tag all resources with appropriate metadata

### Requirement 7: CLI Options

**User Story:** As a user, I want simple CLI options for generating maps locally, so that I can test my flight data before committing.

#### Acceptance Criteria

1. THE System SHALL maintain backward compatibility with the existing render command
2. WHEN a user provides --input-filename, THE System SHALL generate a single Flight Map
3. WHEN a user provides --input-directory, THE System SHALL generate Flight Maps for all JSON files in the directory
4. WHEN a user provides --output-filename, THE System SHALL save a single map to that file
5. WHEN a user provides --output-directory, THE System SHALL save multiple maps to that directory
6. WHEN a user provides --title, THE System SHALL use it as the map title
7. WHERE no title is provided for batch processing, THE System SHALL use the filename as the title

### Requirement 8: Metadata and Organization

**User Story:** As a user, I want my flight maps to be organized with metadata, so that I can track when maps were created and what they represent.

#### Acceptance Criteria

1. WHEN uploading a Flight Map, THE System SHALL include upload timestamp in S3 metadata
2. WHEN uploading a Flight Map, THE System SHALL include the map title in S3 metadata
3. WHEN generating the Index Page, THE System SHALL display the upload date for each Flight Map
4. THE System SHALL generate unique filenames for Flight Maps based on title and timestamp
5. THE System SHALL preserve original filenames when specified by the user

### Requirement 9: Error Handling and Validation

**User Story:** As a developer, I want comprehensive error handling, so that users receive clear feedback when operations fail.

#### Acceptance Criteria

1. WHEN AWS credentials are invalid, THE System SHALL display an authentication error message
2. WHEN a bucket name is invalid, THE System SHALL display a validation error message
3. WHEN network connectivity is unavailable, THE System SHALL display a connection error message
4. WHEN S3 operations fail due to permissions, THE System SHALL display a permissions error message
5. IF Flight Data contains invalid IATA codes, THEN THE System SHALL continue processing valid flights and log warnings for invalid codes
6. WHEN any error occurs, THE System SHALL exit with a non-zero status code
7. WHEN running in GitHub Actions, THE System SHALL output errors in a format compatible with GitHub Actions logging

### Requirement 10: Repository Structure

**User Story:** As a user, I want a clear repository structure for my flight data, so that the GitHub Action knows where to find files.

#### Acceptance Criteria

1. THE System SHALL look for flight data JSON files in a designated directory (e.g., "flights/")
2. WHEN multiple JSON files exist, THE System SHALL process each file as a separate Flight Map
3. WHEN processing multiple files, THE System SHALL use the filename (without extension) as the default map title
4. THE System SHALL support a configuration file specifying which files to process
5. THE System SHALL ignore non-JSON files in the flights directory
