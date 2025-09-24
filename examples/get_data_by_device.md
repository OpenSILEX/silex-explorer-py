# Documentation of `get_data_by_device` function

## Description

The `get_data_by_device` function retrieves measured data for a given device using a GraphQL query and saves the results to a CSV file. The function allows filtering the data based on a specified date range and generates a CSV file with the measured data, including the device URI, target, value, variable, and measurement date. If the CSV file is not needed, the data can still be returned as a pandas DataFrame.

## Arguments

- **session (dict)**:  
  - The authentication session containing the necessary GraphQL endpoint URL and headers for accessing the data.

- **device_uri (str)**:  
  - URI of the device for which the measured data is to be fetched.

- **date_beginning (str, optional)**:  
  - The start date in ISO format (YYYY-MM-DD) to filter the data. If not provided, no filtering by start date is applied.

- **date_end (str, optional)**:  
  - The end date in ISO format (YYYY-MM-DD) to filter the data. If not provided, no filtering by end date is applied.

- **csv_filepath (str, optional)**:  
  - The full file path (including filename) for the CSV output. If not provided, the data will be returned as a dataFrame. The directory will be created automatically if it does not exist.

## Returns

- **pd.DataFrame**:  
  - A DataFrame containing the following columns for each measured data entry:
    - `Device URI`: URI of the device.
    - `Target`: The target of the measured data.
    - `Value`: The value of the measured data.
    - `Variable`: The variable associated with the measured data.
    - `Date`: The date of the measurement.

## Example Usage

```python
from package.exceptions.custom_exceptions import APIRequestError
from package.device.data import get_data_by_device

# Assuming `session` is already defined with authentication details
device_uri = "http://example.com/device/123"  # Replace with actual device URI
date_beginning = "2023-01-01"
date_end = "2023-01-31"
csv_filepath = "/absolute/path/to/output.csv"  # Replace with the desired absolute path
df = get_data_by_device(session, device_uri, date_beginning, date_end, csv_filepath=csv_filepath)
print(df.head())
```

## Expected Output:

The function will return a pandas DataFrame containing the measured data for the specified device, including the following columns:

- `Device URI`: URI of the device.
- `Target`: The target of the measured data.
- `Value`: The value of the measured data.
- `Variable`: The variable associated with the measured data.
- `Date`: The date of the measurement.

Additionally, if csv_filepath is provided, the data will be saved in the specified CSV file.

### Handling Absolute and Relative Paths::
- If csv_filepath is a relative path, the file will be saved relative to the current working directory (os.getcwd()).

- If csv_filepath is an absolute path, the file will be saved at the specified location.

- The function ensures that the directory for the file exists by creating it if necessary (os.makedirs).```
## Error Handling

### APIRequestError:

If the GraphQL request fails (e.g., due to a malformed request, network issues, or server errors), an `APIRequestError` will be raised, providing details about the error.

