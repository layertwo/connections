# Implementation Plan: Flight Map Generator

## Overview

This plan implements batch flight map generation with AWS CDK deployment for static website hosting. The implementation extends the existing CLI tool with batch processing capabilities and adds CDK infrastructure for automated S3 deployment via GitHub Actions.

## Tasks

- [x] 1. Implement batch processing module
  - Create `src/connections/batch.py` with `BatchProcessor` class
  - Implement directory scanning for JSON files
  - Implement batch map generation with error handling
  - Use existing `FlightMap` and `Flight` classes
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

- [ ]* 1.1 Write property test for batch processing completeness
  - **Property 1: Batch Processing Completeness**
  - **Validates: Requirements 2.1, 2.2**

- [ ]* 1.2 Write property test for filename consistency
  - **Property 2: Filename Consistency**
  - **Validates: Requirements 2.3**

- [ ]* 1.3 Write property test for error isolation
  - **Property 3: Error Isolation**
  - **Validates: Requirements 2.5, 2.6, 8.1, 8.2**

- [x] 2. Add batch CLI command
  - Extend `src/connections/main.py` with `batch` command
  - Add `--input-directory` and `--output-directory` options
  - Integrate with `BatchProcessor`
  - Maintain backward compatibility with existing `render` command
  - _Requirements: 6.1, 6.3, 6.5_

- [ ]* 2.1 Write unit tests for batch CLI command
  - Test CLI argument parsing
  - Test integration with BatchProcessor
  - Test backward compatibility

- [x] 3. Implement index page generator
  - Create `src/connections/index.py` with `IndexGenerator` class
  - Create `MapMetadata` dataclass
  - Implement directory scanning for PNG files
  - Implement Jinja2 template rendering
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ]* 3.1 Write property test for index page file generation
  - **Property 4: Index Page File Generation**
  - **Validates: Requirements 4.1, 4.3, 4.4**

- [ ]* 3.2 Write property test for filename to title mapping
  - **Property 5: Filename to Title Mapping in Index**
  - **Validates: Requirements 4.4, 2.3**

- [ ]* 3.3 Write property test for HTML link correctness
  - **Property 10: HTML Link Correctness**
  - **Validates: Requirements 4.3**

- [x] 4. Create HTML template
  - Create `src/connections/templates/index.html.j2`
  - Implement responsive grid layout
  - Add thumbnail previews with clickable links
  - Display map titles
  - _Requirements: 4.2, 4.3, 4.4_

- [x] 5. Add index generation CLI command or script
  - Add command to generate index.html from output directory
  - Can be integrated into batch command or separate script
  - _Requirements: 4.1, 4.5_

- [x] 6. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Create CDK infrastructure
  - Create `cdk/` directory structure
  - Create `cdk/lib/app.ts` as CDK entry point
  - Create `cdk/lib/connections.ts` with S3 bucket, CloudFront, and Route53 configuration
  - Create `cdk/cdk.json` configuration file
  - Create `cdk/package.json` with CDK dependencies
  - Create `cdk/tsconfig.json` for TypeScript configuration
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 5.10_

- [ ]* 7.1 Write CDK stack tests
  - Test bucket configuration (website hosting, public access)
  - Test BucketDeployment construct
  - Use CDK assertions library

- [ ]* 7.2 Write property test for CDK deployment completeness
  - **Property 6: CDK Deployment Completeness**
  - **Validates: Requirements 3.4, 3.5**

- [ ] 8. Implement directory creation utility
  - Add utility function to create output directories if they don't exist
  - Integrate into BatchProcessor
  - _Requirements: 8.3_

- [ ]* 8.1 Write property test for directory creation
  - **Property 9: Directory Creation**
  - **Validates: Requirements 8.3**

- [ ] 9. Create GitHub Actions workflow
  - Create `.github/workflows/deploy.yml`
  - Configure trigger on push to main with changes in `flights/`
  - Add steps for Python/Poetry setup
  - Add step to generate flight maps
  - Add step to generate index page
  - Add steps for Node.js/CDK setup
  - Add step for CDK deployment
  - Configure AWS credentials (OIDC or secrets)
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

- [ ] 10. Add sample flight data
  - Create `flights/` directory
  - Add sample JSON files for testing
  - _Requirements: 9.1, 9.2_

- [ ] 11. Update dependencies
  - Add `jinja2` to pyproject.toml
  - Add `hypothesis` to dev dependencies
  - Update README with new batch command usage
  - _Requirements: All_

- [ ] 12. Create .gitignore entries
  - Add `output/` directory to .gitignore
  - Add `cdk.out/` to .gitignore
  - Add CDK-specific ignores

- [ ] 13. Final checkpoint - Integration testing
  - Test end-to-end batch processing locally
  - Test index generation with sample data
  - Test CDK synthesis (`cdk synth`)
  - Verify CloudFormation template
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- CDK tests ensure infrastructure is correctly defined
