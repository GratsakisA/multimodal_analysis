# Multimodal Analysis

⚠️ **Status:** Early development (not yet released)

## Overview

`multimodal_analysis` processes and analyzes behavioral data from multimodal **audiovisual** experiments. It provides streamlined tools for comparing behavior across conditions, modalities, and subjects, with built-in visualization and database support.

## Features

* Behavioral data processing and analysis
* Analysis across experimental modalities
* Analysis across animals
* Database integration with DataJoint
* Configurable behavioral sessions
* Data visualization
* Reusable analysis functions and utilities
* Jupyter notebook-based analysis workflows
* Optional support for running EthoPy behavioral task configurations

## Repository Structure

<!-- BEGIN REPOSITORY TREE -->

<!-- END REPOSITORY TREE -->

## Get started using multimodal_analysis

1. Clone the repository and move into the project directory:

   ```bash
   git clone https://github.com/GratsakisA/multimodal_analysis.git
   cd multimodal_analysis
   ```

2. Install the project and its core dependencies:

   ```bash
   uv sync
   ```

   > This creates a project-specific virtual environment in `.venv` and installs the dependencies specified in `pyproject.toml` and `uv.lock`.

### Optional: Install EthoPy task dependencies

If you want to run the behavioral task configurations located in `task_configurations/`, install the optional `tasks` dependencies:

```bash
uv sync --extra tasks
```

This installs EthoPy and its required Python dependencies.

> **Note:** The EthoPy plugin repository required by some task configurations is not currently installed automatically. Instructions for installing and configuring the required plugins will be added separately.

## How to Contribute

This project is actively being developed.

* File issues for bugs or feature requests.
* Pull requests are welcome. Please check with the maintainers before making larger changes.
