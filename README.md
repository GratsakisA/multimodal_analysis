# Multimodal Analysis

[![Latest Release](https://img.shields.io/github/v/release/GratsakisA/multimodal_analysis)](https://github.com/GratsakisA/multimodal_analysis/releases)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)

**Status:** Early development. The initial release, `v0.1.0`, is available.

## Overview

`multimodal_analysis` provides tools for processing and analyzing behavioral data from multimodal **audiovisual experiments**. It supports comparisons across experimental conditions, modalities, and animals, with visualization, database integration, and configurable behavioral-session management.

The project is under active development, and its functionality and API may change between releases.

## Features

- Behavioral data processing and analysis
- Analysis across experimental conditions and modalities
- Analysis across animals
- Database integration with DataJoint
- Configurable behavioral sessions
- Data visualization
- Reusable analysis functions and utilities
- Jupyter notebook-based analysis workflows
- Optional support for EthoPy behavioral task configurations

## Repository Structure

<!-- BEGIN REPOSITORY TREE -->

<!-- END REPOSITORY TREE -->

## Getting Started

### Prerequisites

- Python 3.11 or later
- [uv](https://docs.astral.sh/uv/) for environment and dependency management

### Installation

Clone the repository and install the project with its dependencies:

```bash
git clone https://github.com/GratsakisA/multimodal_analysis.git
cd multimodal_analysis
uv sync
```

This creates a project-specific virtual environment in `.venv` and installs the dependencies specified in `pyproject.toml` and `uv.lock`.

### Optional: EthoPy Task Dependencies

If you want to use the behavioral task configurations in `task_configurations/`, install the optional `tasks` dependencies:

```bash
uv sync --extra tasks
```

This installs EthoPy and its required Python dependencies.

> **Note:** The EthoPy plugin repository required by some task configurations is not installed automatically. Instructions for installing and configuring the required plugins will be provided separately.

## Releases

Released versions and their changelogs are available on the [GitHub Releases page](https://github.com/GratsakisA/multimodal_analysis/releases).

The project follows semantic versioning, with release versions managed by [Python Semantic Release](https://python-semantic-release.readthedocs.io/).

## Contributing

Contributions, bug reports, and feature requests are welcome.

- Open an issue to report a bug or suggest an improvement.
- Submit a pull request for proposed changes.
- Please discuss substantial changes with the maintainers before starting work.