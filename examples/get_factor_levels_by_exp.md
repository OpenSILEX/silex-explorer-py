# Documentation of `get_fl_by_exp` function

## Description

The `get_fl_by_exp` function retrieves all factors and their associated levels for a given experiment using a GraphQL API. It then exports the retrieved data into a CSV file for further analysis. The function handles the process of fetching factors, their levels, and saving the results into a CSV file (default filename: `factor_levels.csv`). The CSV file is saved in the `temp_files` directory.

## Arguments

- **session (dict)**:  
  - The authentication session containing the necessary authentication token and headers to access the GraphQL API.

- **experiment_uri (str)**:  
  - URI of the experiment for which the factors and their levels are to be fetched.

- **csv_filename (str, optional)**:  
  - The filename for the output CSV file. The default is `'factor_levels.csv'`. The file will be saved in the `temp_files` directory.

## Returns

- **pd.DataFrame**:  
  - A DataFrame containing the factors, their URIs, and associated factor levels with their URIs:
    - `Factor`: The name of the factor.
    - `Factor URI`: The URI of the factor.
    - `Factor level`: The name of the factor level.
    - `Factor level URI`: The URI of the factor level.

## Example Usage

```python
from package.exceptions.custom_exceptions import APIRequestError
from package.factor.ls_fl_factor import get_fl_by_exp

# Assuming `session` is already defined with authentication details
experiment_uri = "https://example.com/experiment/123"  # Replace with the actual experiment URI
df = get_fl_by_exp(session, experiment_uri, csv_filename='factor_levels.csv')
print(df.head())
```
## Expected Output:
The function will return a pandas DataFrame containing the factors and their levels related to the experiment, including both the factor and level URIs. Additionally, the data will be saved in a CSV file named factor_levels.csv inside the temp_files directory.
### Directory Structure for CSV File:
```txt
project_root/
    ├── temp_files/
        └── factor_levels.csv
```

## Error Handling
### APIRequestError:
If any GraphQL request fails (due to a malformed request, connection error, or any other issue with the server), an APIRequestError exception will be raised with the corresponding error message.