
<div align="center">

# SilexExplorerR
###  R Interface for OpenSILEX Platform

[![Python](https://img.shields.io/badge/Python-%3E%3D%203.0-blue?style=flat-square&logo=python)](https://www.python.org/)
[![OpenSILEX](https://img.shields.io/badge/OpenSILEX-Platform-green?style=flat-square)](https://opensilex.org/)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg?style=flat-square)](https://opensilex.org/documentation)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?style=flat-square&logo=github)](https://github.com/OpenSILEX/silex-explorer-py)

[Documentation](https://opensilex.org/documentation) • 
[Installation Guide](#installation) • 
[Quick Start](#quick-start) • 
[Examples](./examples) • 
[Contributing](#contributing)
---
</div>

# **SilexExplorerPy**
> **Brief Description**: A Python package designed to help researchers extract, visualize, and analyze complex phenotypic and environmental data for in-depth scientific insights.

## **Table of Contents**

- [Description](#description)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Contributing](#contributing)

## **Description**
`SilexExplorerPy` is a Python package designed to help researchers extract, visualize, and analyze complex phenotypic and environmental data associated with scientific experiments. It provides a comprehensive set of tools for interacting with OpenSILEX instances to retrieve experimental data, manage scientific objects, and collect environmental information. Ideal for researchers in fields such as agriculture and environment, this package enables efficient data management and filtering by experiments, species, projects, and environmental conditions. It also supports exporting, visualizing, and analyzing the results, facilitating in-depth scientific insights and data-driven decision-making.

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

## **Installation**
1. Make sure you have Python 3.7+ installed:  
 To check the version of Python installed on your system, run the following command:

    ```bash
    python3 --version
    ```
    It should display something like:
    ```bash
    Python 3.8.10
    ```
2. Install the package using pip from ForgeMIA:  
  To install the package directly from ForgeMIA, use the following command:
   ```bash
   pip3 install git+https://forgemia.inra.fr/OpenSILEX/opensilex-graphql/python-package.git

3. Install additional dependencies:
   ```bash
   pip3 install -r requirements.txt

## **Quick Start**
Here's a basic example of how to use the package:
```python
from package.exceptions.custom_exceptions import APIRequestError, AuthenticationError
from package.auth.auth import login
from package.experiment.ls_exp import get_ls_exp

# Configuration for the OpenSILEX server (demo instance)
        username = "admin@opensilex.org"
        password = "******"  # Enter your password here
        instance_rest = "138.102.159.36"
        instance_name = "demo"
        port_rest = "8084"
        instance_graphql = "138.102.159.37"
        
        # Login to the OpenSILEX instance
        session = login(username, password, instance_rest, instance_name, port_rest, instance_graphql)

        # Get the list of experiments and save to CSV (in temp_files)
        df_exp = get_ls_exp(session)
```
## **Project Structure**

```
project/
│
├── docs/ — Documentation for the package
├── examples/ — Usage examples
├── package/ — Source code organized into modules
│ ├── auth/ — Authentication management
│ ├── device/ — Device management
│ ├── exceptions/ — Custom error handling
│ ├── experiment/ — Experiment management
│ ├── facility/ — Facility management
│ ├── factor/ — Factor management
│ └── scientific_object/ — Scientific object management
├── temp_files/ — Temporary files generated by the package
├── tests/ — Unit and functional tests
├── main.py — Main script
├── README.md — General documentation
├── requirements.txt — Project dependencies
└── setup.py — Installation script
```
## **Contributing**

Contributions are welcome!

1. Fork the repository.  
2. Create a branch for your changes:  
   ```bash
   git checkout -b feature/my-new-feature
3. Commit your changes and push them:
   ```bash
   git push origin feature/my-new-feature
4. Open a pull request.