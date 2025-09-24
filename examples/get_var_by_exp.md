# Documentation of `get_ls_var_by_exp` function

## Description

The `get_ls_var_by_exp` function retrieves all variables associated with a specific experiment using an API request. It sends a GET request to the REST API, fetches the variables, and stores the results in a CSV file. The function handles pagination automatically and saves the data in a file named `variables.csv` (or any custom filename provided) inside the `temp_files` directory.

## Arguments

- **session (dict)**:  
  - The authentication session containing the necessary API endpoint URL and headers for accessing the data.

- **experiment_uri (str)**:  
  - URI of the experiment for which variables are to be fetched.

- **page_size (int, optional)**:  
  - Number of items per page for pagination. The default value is 20. It can be adjusted to handle a larger or smaller dataset.

- **csv_filename (str, optional)**:  
  - The filename for the output CSV file. The default filename is `'variables.csv'`.

## Returns

- **pd.DataFrame**:  
  - A DataFrame containing the variables related to the experiment, along with their associated metadata:
    - `uri`: URI of the variable.
    - `name`: Name of the variable.
    - `entity_name`: Name of the associated entity.
    - `characteristic_name`: Name of the associated characteristic.
    - `method_name`: Name of the associated method.
    - `unit_name`: Name of the associated unit.

## Example Usage

```python
from package.exceptions.custom_exceptions import APIRequestError
from package.experiment.ls_var_exp import get_ls_var_by_exp

# Assuming `session` is already defined with authentication details
experiment_uri = "https://example.com/experiment/123"  # Replace with the actual experiment URI
df = get_ls_var_by_exp(session, experiment_uri, page_size=20, csv_filename='variables.csv')
print(df.head())
```
## Expected Output:
The function will return a pandas DataFrame containing the variables related to the specified experiment, including their URI, name, entity, characteristic, method, and unit. Additionally, the data will be saved in a CSV file named variables.csv inside the temp_files directory.

### Directory Structure for CSV File:
```txt
project_root/
    ├── temp_files/
        └── variables.csv
```

## Error Handling
### APIRequestError:
If any API request fails (e.g., due to a malformed request, network issues, or server errors), an APIRequestError will be raised, providing details about the error.