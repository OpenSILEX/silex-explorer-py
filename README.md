<div align="center">

# SilexExplorerPy

### Python Interface for OpenSILEX Platform

[![Python](https://img.shields.io/badge/Python-%3E%3D%203.12-blue?style=flat-square&logo=python)](https://www.python.org/)
[![OpenSILEX](https://img.shields.io/badge/OpenSILEX-Platform-green?style=flat-square)](https://opensilex.org/)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg?style=flat-square)](https://opensilex.org/documentation)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?style=flat-square&logo=github)](https://github.com/OpenSILEX/silex-explorer-py)

[Documentation](https://opensilex.org/documentation) •
[Installation](#installation) •
[Quick Start](#quick-start) •
[Examples](./examples) •
[Development](#development) •
[Contributing](#contributing)

---

</div>

## Description

`SilexExplorerPy` is a Python package designed to help researchers extract, visualize, and analyze complex phenotypic and environmental data associated with scientific experiments.

It provides tools for interacting with OpenSILEX instances to retrieve experimental data, manage scientific objects, collect environmental information, export results, and support further analysis and visualization.

## Features

- **User Authentication**  
  Authenticate to an OpenSILEX instance and prepare REST and GraphQL access through `login`.

- **Experiment Retrieval and Filtering**  
  Retrieve experiments with `get_ls_exp`, filter them using experiment metadata, return results as pandas DataFrames, and optionally export them to CSV.

- **Scientific Object Types Retrieval**  
  Retrieve scientific object types associated with an experiment using `get_ls_os_types_by_exp`.

- **Factors and Factor Levels Retrieval**  
  Retrieve factors and their associated levels for an experiment using `get_fl_by_exp`.

- **Variables Retrieval by Experiment**  
  Retrieve variables and their metadata for an experiment using `get_ls_var_by_exp`.

- **Scientific Objects Retrieval by Experiment**  
  Retrieve scientific objects associated with an experiment and object type using `get_os_by_exp`, with optional factor-level and germplasm filtering.

- **Data Retrieval by Variable**  
  Retrieve experimental data associated with scientific objects and variables using `get_data_by_variable`.

- **Environmental Variables by Facility**  
  Retrieve environmental variables linked to a facility using `get_variable_by_facility`.

- **Environmental Data by Facility**  
  Retrieve environmental data for a facility and date range using `get_environmental_data_by_facility`.

- **Devices by Facility**  
  Retrieve devices associated with a facility using `get_devices_by_facility`.

- **Measured Data by Device**  
  Retrieve measured data associated with a device using `get_data_by_device`.

- **Moves for Scientific Objects**  
  Retrieve the movement history of a scientific object using `get_moves_by_os`.

## Installation

### Requirements

SilexExplorerPy requires **Python 3.12 or later**:

```toml
requires-python = ">=3.12"
```

Check your Python version with:

```bash
python --version
```

This project uses [uv](https://docs.astral.sh/uv/) for Python environment and dependency management.

### Install SilexExplorerPy from the Git repository

Create a virtual environment:

```bash
uv venv
```

Activate the environment on Linux or macOS:

```bash
source .venv/bin/activate
```

Install SilexExplorerPy from the Git repository:

```bash
uv pip install "git+ssh://git@forge.inrae.fr/OpenSILEX/opensilex-graphql/silex-explorer-py.git"
```

The SSH command requires access to the repository and a correctly configured SSH key.

Once installed, you can run a script inside the environment with:

```bash
uv run python script.py
```

## Quick Start

```python
from silexexplorerpy.auth import login
from silexexplorerpy.exceptions import APIRequestError, AuthenticationError
from silexexplorerpy.experiment import get_ls_exp


def main():
    try:
        username = "your_username"
        password = "your_password"
        instance_rest = "https://your-opensilex-instance/rest"
        url_graphql = "https://your-opensilex-instance/graphql"

        session = login(
            username,
            password,
            instance_rest,
            url_graphql,
        )

        experiments = get_ls_exp(session)
        print(experiments.head())

    except AuthenticationError as exc:
        print(f"Authentication error: {exc}")
    except APIRequestError as exc:
        print(f"API request error: {exc}")


if __name__ == "__main__":
    main()
```

Run the script with:

```bash
uv run python main.py
```

### Important note about name-based filtering

For functions that filter using names or labels, the corresponding elements must first be loaded into the internal URI/name table.

For example:

```python
get_os_by_exp(session, experiment_name, obj_type_name)
```

Before filtering scientific objects by experiment and object-type names, first load the required information:

```python
get_ls_exp(session=session)
get_ls_os_types_by_exp(session, experiment_name="ZA17")
```

This makes the corresponding names and URIs available to functions that perform name-based filtering.

## Development

This section is for contributors who want to work on the SilexExplorerPy source code.

### Setup

Clone the repository:

```bash
git clone git@forge.inrae.fr:OpenSILEX/opensilex-graphql/silex-explorer-py.git
cd silex-explorer-py
```

Install the project and synchronize its dependencies:

```bash
uv sync
```

`uv sync` creates or updates the project environment according to `pyproject.toml` and `uv.lock`.

### Building the package

Build the source distribution and wheel:

```bash
uv build
```

The generated distributions are written to the `dist/` directory.

## Project Structure

```text
silex-explorer-py/
├── examples/
│   ├── authentication.md
│   ├── get_data_by_device.md
│   ├── get_devices_by_facility.md
│   ├── get_env_var_by_facility.md
│   ├── get_experiment_list.md
│   ├── get_factor_levels_by_exp.md
│   ├── get_os_by_exp.md
│   ├── get_os_types_by_exp.md
│   └── get_var_by_exp.md
├── src/
│   ├── pyscaf/
│   │   └── documentation/
│   │       └── scripts/
│   └── silexexplorerpy/
│       ├── auth/
│       ├── device/
│       ├── exceptions/
│       ├── experiment/
│       ├── facility/
│       ├── factor/
│       ├── scientific_object/
│       ├── uri_name_manager/
│       ├── visualisation/
│       └── __init__.py
├── tests/
├── data/
├── LICENSE
├── README.md
├── pyproject.toml
└── uv.lock
```

## Contributing

Contributions are welcome.

1. Fork or clone the repository.
2. Create a branch for your changes:

   ```bash
   git checkout -b feature/my-new-feature
   ```

3. Make your changes.

4. Commit your changes:

   ```bash
   git add .
   git commit -m "Describe your changes"
   ```

5. Push your branch and open a pull request.
