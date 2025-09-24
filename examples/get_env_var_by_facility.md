# Documentation of `get_variable_by_facility` function

## Description

The `get_variable_by_facility` function retrieves environmental variable information for a specific facility within a given date range using a GraphQL API request. It fetches the variables linked to the facility, handles date filtering, and stores the results in a CSV file. The function also handles pagination and ensures the output is saved to a file named `facility_env_var.csv` (or any custom filename provided) inside the `temp_files` directory.

## Arguments

- **session (dict)**:  
  - The authentication session containing the necessary GraphQL endpoint URL and headers for accessing the data.

- **facility_uri (str)**:  
  - URI of the facility for which environmental variables are to be fetched.

- **date_beginning (str, optional)**:  
  - Start date for filtering the data (format: `YYYY-MM-DD`). If not provided, it defaults to the current date.

- **date_end (str, optional)**:  
  - End date for filtering the data (format: `YYYY-MM-DD`). If not provided, it defaults to the current date.

- **csv_filename (str, optional)**:  
  - The filename for the output CSV file. The default filename is `'facility_env_var.csv'`.

## Returns

- **pd.DataFrame**:  
  - A DataFrame containing detailed environmental variable information for the specified facility, including the following columns:
    - `uri`: URI of the variable.
    - `name`: Name of the variable.
    - `entity_name`: Name of the associated entity.
    - `characteristic_name`: Name of the associated characteristic.
    - `method_name`: Name of the associated method.
    - `unit_name`: Name of the associated unit.

## Example Usage

```python
from package.exceptions.custom_exceptions import APIRequestError
from package.facility.env_var import get_variable_by_facility

# Assuming `session` is already defined with authentication details
facility_uri = "http://phenome.inrae.fr/m3p/id/organization/facility.test1"# Replace with the actual facility URI
date_beginning = "2023-01-01"
date_end = "2023-01-31"

# Fetch variable details and save the result in a CSV file
df = get_variable_by_facility(session, facility_uri, date_beginning, date_end, csv_filename="facility_env_var.csv")
print(df.head())
```

## Expected Output:

The function will return a pandas DataFrame containing the detailed environmental variables associated with the facility, including their URI, name, entity, characteristic, method, and unit. Additionally, the data will be saved in a CSV file named `facility_env_var.csv` inside the `temp_files` directory.

### Directory Structure for CSV File:

```txt
project_root/
    ├── temp_files/
        └── facility_env_var.csv
```
## Error Handling

### APIRequestError:

If any GraphQL request fails (e.g., due to a malformed request, network issues, or server errors), an `APIRequestError` will be raised, providing details about the error.
