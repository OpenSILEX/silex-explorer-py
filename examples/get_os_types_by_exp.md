# Documentation of `get_ls_os_types_by_exp` function

## Description

The `get_ls_os_types_by_exp` function retrieves all scientific object types associated with a given experiment using pagination. It fetches the data from a REST API and exports the results into a CSV file for further analysis. This function handles pagination automatically and saves the data into a file named `scientific_object_types.csv` (or any custom name provided).

## Arguments

- **session (dict)**: 
    - The authentication session containing the required authentication token and headers to access the REST API.
    
- **experiment_uri (str)**: 
    - URI of the experiment for which scientific object types are to be fetched.
    
- **page_size (int, optional)**: 
    - Number of items per page for pagination. The default value is 20. It can be adjusted based on the number of results expected.
    
- **csv_filename (str, optional)**: 
    - The filename for the output CSV file. The default is `'scientific_object_types.csv'`.

## Returns

- **pd.DataFrame**: 
    - A DataFrame containing the scientific object types' URIs and Names:
        - `Uri`: URI of the scientific object type.
        - `Name`: Name of the scientific object type.


## Example Usage

```python
from package.exceptions.custom_exceptions import APIRequestError
from package.experiment.ls_os_type_exp import get_ls_os_types_by_exp

# Assuming `session` is already defined with authentication details
experiment_uri = "https://example.com/experiment/123"  # Replace with the actual experiment URI
df = get_ls_os_types_by_exp(session, experiment_uri, page_size=20, csv_filename='scientific_object_types.csv')
print(df.head())
```
### Expected Output:
The function will return a pandas DataFrame containing the scientific object types related to the experiment, including the URI and name. Additionally, the data will be saved in a CSV file named scientific_object_types.csv inside the temp_files directory.

### Directory Structure for CSV File:
```txt
project_root/
    ├── temp_files/
        └── scientific_object_types.csv
```
## Error Handling
### APIRequestError:
If the API request fails (due to a malformed request, connection error, or any other issue with the server), an APIRequestError exception will be raised with the corresponding error message.