# TEMP - TO BE CHANGED WITH MY NEW PR - Development Guide

This document provides instructions for developers working on the `mcp-server-motherduck` project.

## Setup development environment

1. Clone the repository
2. Install dependencies using [uv](https://github.com/astral-sh/uv):
   ```bash
   uv sync
   ```

## Testing

To test the MCP server locally:

1. Install the package in development mode:
   ```bash
   pip install -e .
   ```

2. Run the server manually:
   ```bash
   mcp-server-motherduck
   ```

3. For testing with Claude Desktop, add the configuration snippet from the README.md to your Claude Desktop config file.

### Manual Testing

You can test your MCP server with Claude by:

1. Configuring Claude Desktop to use your local server
2. Creating a conversation with Claude
3. Testing the provided prompts and tools:
   - duckdb-motherduck-prompt
   - query tool

## Release process

To release a new version:

1. Update the version in `pyproject.toml`
2. Create and push a new tag matching the version with a 'v' prefix:
   ```bash
   git tag v0.3.4
   git push origin v0.3.4
   ```
3. GitHub Actions will automatically:
   - Extract the version from the tag
   - Update version numbers in the codebase
   - Build the package
   - Publish the package to PyPI

## CI/CD pipeline

The project uses GitHub Actions for continuous integration and deployment:

- The workflow is defined in `.github/workflows/publish.yml`
- It's triggered when a new release is published
- It automatically builds and publishes the package to PyPI
