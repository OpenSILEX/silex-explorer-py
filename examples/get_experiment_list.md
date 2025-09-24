# Documentation of `get_ls_exp` function

## Description

The `get_ls_exp` function retrieves a list of experiments from the server using a GraphQL query, with optional filters applied for species, project and date. The filters are not required to be used together and can be applied individually. The function then flattens the species and project information for better readability and finally exports the filtered data into a CSV file for further analysis.

## Arguments

- **session (dict)**: 
    - The authentication session containing the required authentication token and headers to access the GraphQL API.
    
- **species_uri (str, optional)**: 
    - URI of the species to filter experiments by. Default is `None`.
    
- **project_uri (str, optional)**: 
    - URI of the project to filter experiments by. Default is `None`.
    
- **active_date (str, optional)**: 
    - Specific date to check active experiments in `YYYY-MM-DD` format. Default is `None`.
    
- **species_name (str, optional)**: 
    - Name of the species to filter experiments by. Default is `None`.
    
- **project_name (str, optional)**: 
    - Name of the project to filter experiments by. Default is `None`.
    
- **csv_filename (str, optional)**: 
    - Name of the CSV file to save the resulting experiments data. Default is `'list_experiments.csv'`.

## Returns

- **pd.DataFrame**: 
    - A DataFrame containing the experiments that match the filtering criteria, including:
        - `_id`: ID of the experiment.
        - `label`: The label of the experiment.
        - `startDate`: Start date of the experiment.
        - `endDate`: End date of the experiment.
        - `hasSpecies`: The species associated with the experiment.
        - `hasProject`: The project associated with the experiment.

## Filters and Their Effect

This function supports several filters that can be applied individually or in combination to narrow down the results:

### 1. **species_uri (str)**
- **Description**: Filters experiments based on the URI of the species.
- **Example Usage**: 
    ```python
    df = get_ls_exp(session=session, species_uri="http://example.com/species/123")
    ```
    This will return all experiments associated with the species URI "http://example.com/species/123".

### 2. **project_uri (str)**
- **Description**: Filters experiments based on the URI of the project.
- **Example Usage**: 
    ```python
    df = get_ls_exp(session=session, project_uri="http://example.com/project/456")
    ```
    This will return all experiments associated with the project URI "http://example.com/project/456".

### 3. **active_date (str, `YYYY-MM-DD`)**
- **Description**: Filters experiments by the specific date in `YYYY-MM-DD` format. Only experiments that are active on the given date (i.e., the start date is before or equal to the date, and the end date is after or equal to the date) will be included.
- **Example Usage**: 
    ```python
    df = get_ls_exp(session=session, active_date="2023-01-01")
    ```
    This will return all experiments active on January 1, 2023.

### 4. **species_name (str)**
- **Description**: Filters experiments based on the name of the species. This performs a case-insensitive search.
- **Example Usage**: 
    ```python
    df = get_ls_exp(session=session, species_name="Arabidopsis")
    ```
    This will return all experiments associated with species that include the name "Arabidopsis".

### 5. **project_name (str)**
- **Description**: Filters experiments based on the name of the project. This performs a case-insensitive search.
- **Example Usage**: 
    ```python
    df = get_ls_exp(session=session, project_name="Plant Research")
    ```
    This will return all experiments associated with projects that include the name "Plant Research".

### 6. **csv_filename (str)**
- **Description**: The name of the CSV file where the filtered results will be saved. The default is `'list_experiments.csv'`. The file will be saved in the `temp_files` directory at the root of the project.

## Example Usage

```python
from package.exceptions.custom_exceptions import APIRequestError
from package.experiment.ls_exp import get_ls_exp 

df = get_ls_exp(
    session=session,
    species_uri="http://example.com/species/123",
    project_uri="http://example.com/project/456",
    active_date="2023-01-01",
    species_name="Arabidopsis",
    project_name="Plant Research",
    csv_filename="filtered_experiments.csv"
)
print(df.head())
```

### Expected Output:
The function will return a pandas DataFrame with the filtered list of experiments based on the provided parameters. It will also save the results to a CSV file named "filtered_experiments.csv".

### Directory Structure for CSV File:
```txt
project_root/
    ├── temp_files/
        └── filtered_experiments.csv
```

## Error Handling
### APIRequestError:

    If the GraphQL request fails (due to a malformed request, connection error, or any other issue with the server), an APIRequestError exception will be raised with the corresponding error message.
