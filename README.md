<div align="center">

# SilexExplorerPy

### Python Interface for OpenSILEX Platform

[![Python](https://img.shields.io/badge/Python-%3E%3D%203.12-blue?style=flat-square&logo=python)](https://www.python.org/)
[![OpenSILEX](https://img.shields.io/badge/OpenSILEX-Platform-green?style=flat-square)](https://opensilex.org/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?style=flat-square&logo=github)](https://github.com/OpenSILEX/silex-explorer-py)

[Description](#description) •
[Installation](#installation) •
[Quick Start](#quick-start) •
[Examples](./examples) •
[Development](#development) •
[Contributing](#contributing)

---

</div>

## **Description**

`SilexExplorerPy` is a Python package designed to help researchers extract, visualize, and analyze complex phenotypic and environmental data associated with scientific experiments. It provides a comprehensive set of tools for interacting with OpenSILEX instances to retrieve experimental data and collect environmental information. Ideal for researchers in fields such as agriculture and environment, this package enables efficient data exploration and filtering by experiments, species, projects, and environmental conditions. It also supports exporting, visualizing, and analyzing the results, facilitating in-depth scientific insights and data-driven decision-making.

## **Features**
- **User Authentication**:   
  The `login` function allows secure authentication to an OpenSILEX instance and facilitates seamless interaction with its REST and GraphQL services by:  
  - Providing a token-based authentication mechanism.  
  - Configuring and generating REST and GraphQL endpoints dynamically.  
  - Preparing headers for secure and efficient API communication.  
  - Supporting custom ports and flexible server setups.  
 
- **Experiment Retrieval and Filtering**:   
  The `get_ls_exp` function allows you to retrieve and filter experiments from an OpenSILEX instance using a GraphQL query. Key features include:  
  - Filtering experiments by species_uri, project_uri, date,species_name or project name.    
  - Returning results as a pandas DataFrame. 
  - Exporting filtered results to a CSV file for further analysis.  

- **Scientific Object Types Retrieval**:    
  The `get_ls_os_types_by_exp` function retrieves all scientific object types associated with a specific experiment from an OpenSILEX instance. Key features include:   
  - Filtering scientific object types by experiment URI.  
  - Returning results, including URIs and namesas,as a pandas DataFrame.  
  - Exporting results, to a CSV file.  

- **Factors and Factor Levels Retrieval** :   
  The `get_fl_by_exp` function retrieves all factors and their associated levels for a given experiment. Key features include:  
  - Retrieving factors and their levels using GraphQL queries.  
  - Storing the retrieved data, including factor URIs and level URIs, in a CSV file.  
  - Returning the results as a pandas DataFrame for further analysis or processing.  

- **Variables Retrieval by Experiment**:   
  The `get_ls_var_by_exp` function retrieves all variables for a given experiment. Key features include:  
  - Fetching variables and their associated metadata (e.g., entity, characteristic, method, and unit) for a specified experiment.  
  - Saving the retrieved data to a CSV file for further analysis.  
  - Returning the variables as a pandas DataFrame.   

- **Scientific Objects Retrieval by Experiment**:   
  The `get_os_by_exp` function retrieves scientific objects and their associated details for a given experiment and object type. Key features include:  
  - Dynamic filtering for factor levels and germplasm (both by uri and name).  
  - Supporting GraphQL queries to fetch detailed information about the scientific objects, including factors and germplasm data.  
  - Saving the retrieved data to a CSV file for further analysis.  
  - Returning the data as a pandas DataFrame, with optional filters applied for factor levels and germplasm.

- **Data Retrieval by Variable**:   
  The `get_data_by_variable` function retrieves data associated with scientific objects for a specified experiment and object type. Key features include:  
  - Supports optional filtering by factor levels and germplasm.  
  - Extracts data such as target, variable, value, and date for each scientific object.  
  - Organizes the extracted data by variable and exports each variable's data to separate CSV files.  
  - Returns a dictionary where keys are variable names and values are DataFrames containing the associated data.  
  - The data can be filtered based on a provided list of variables (e.g., sensor readings, measurements).  
  - Saves the CSV files in the `temp_files` directory.

- **Environmental Variables by Facility**:   
  The `get_variable_by_facility` function retrieves detailed environmental variable information linked to a facility. Key features include:  
  - Allows filtering by a specific date range (optional).  
  - Fetches a list of unique variables associated with the facility for the given date range.  
  - Retrieves detailed information for each variable (e.g., entity, characteristic, method, unit).  
  - Saves the variable details into a CSV file (default: `facility_env_var.csv`).  
  - Returns the variable details as a DataFrame. 

- **Retrieve and Export Environmental Data by Facility**:   
  The `get_environmental_data_by_facility` function fetches environmental data for a specific facility within a given date range. Key features include:  
  - Retrieves environmental data and exports it to CSV files, organized by variable.  
  - Allows filtering by a list of environmental variables (optional). If none provided, variables are fetched using `get_variable_by_facility`.  
  - Supports flexible date filtering (defaulting to today's date if no dates are provided).  
  - The data is saved as separate CSV files for each variable, with a customizable prefix.  
  - Returns a dictionary where keys are variable names and values are corresponding DataFrames. 

- **Retrieve and Export Devices by Facility**:   
  The `get_devices_by_facility` function fetches devices associated with a specific facility using pagination. Key features include:  
  - Retrieves devices data for a given facility with pagination support.  
  - Each device is represented with its URI, type, and name. 
  - Saves the retrieved devices data to a CSV file.  
  - Returns a list of dictionaries containing device details.  

- **Retrieve Measured Data by Device**:   
  The `get_data_by_device` function retrieves measured data associated with a specific device and exports it to a CSV file. Key features include:  
  - Fetches measured data for a device based on a specified date range (optional).  
  - Data includes device URI, target, value, variable, and measurement date.  
  - Saves the data to a CSV file, with a customizable filename.  
  - Returns the data as a Pandas DataFrame.  

- **Retrieve and Export Moves for a Scientific Object**:  
  The `get_moves_by_os` function retrieves the movement history of a scientific object and exports it to a CSV file. Key features include:  
  - Retrieves moves based on the object's URI, experiment, and optional date range.  
  - The moves include information about the "from" and "to" locations and the start and end times of each move.  
  - Generates a CSV file with columns: From, To, HasBeginning, and HasEnd.  
  - Returns a list of moves, each containing the relevant details.  

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
from silex_explorer_py.auth import login
from silex_explorer_py.exceptions import APIRequestError, AuthenticationError
from silex_explorer_py.experiment import get_ls_exp


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
