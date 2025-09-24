# Documentation of `get_devices_by_facility` function

## Description

The `get_devices_by_facility` function retrieves all devices associated with a given facility through a REST API request. The function handles pagination automatically and stores the results in a CSV file. It returns a list of devices where each device is represented by a dictionary containing its URI, type, and name. The data is also saved to a file named `devices.csv` (or any custom filename provided).

## Arguments

- **session (dict)**:  
  - The authentication session containing the necessary REST API endpoint URL and headers for accessing the data.

- **facility_uri (str)**:  
  - URI of the facility for which devices are to be fetched.

- **page_size (int, optional)**:  
  - Number of items per page for pagination. The default value is 20. It can be adjusted to handle larger or smaller datasets.

- **csv_filename (str, optional)**:  
  - The filename for the output CSV file. The default filename is `'devices.csv'`.

## Returns

- **list**:  
  - A list of dictionaries where each dictionary represents a device and contains:
    - `uri`: URI of the device.
    - `type`: Type of the device (e.g., Sensor, Actuator).
    - `name`: Name of the device.

## Example Usage

```python
from package.exceptions.custom_exceptions import APIRequestError
from package.facility.devices import get_devices_by_facility

# Assuming `session` is already defined with authentication details
facility_uri = "http://phenome.inrae.fr/m3p/id/organization/facility.test"  # Replace with the actual facility URI
devices = get_devices_by_facility(session, facility_uri)

# This will retrieve device data associated with the facility and return a list like:
# [{'uri': '/devices/1', 'type': 'Sensor', 'name': 'Temperature Sensor'},
#  {'uri': '/devices/2', 'type': 'Sensor', 'name': 'Humidity Sensor'}]
## Expected Output:
```
The function will return a list of dictionaries representing the devices associated with the specified facility, including each device's URI, type, and name. Additionally, the data will be saved in a CSV file named `devices.csv` (or any custom filename) inside the current working directory.

### Directory Structure for CSV File:

```txt
project_root/
    ├── devices.csv
```
## Error Handling

### APIRequestError:

If the API request fails (e.g., due to a malformed request, network issues, or server errors), an `APIRequestError` will be raised, providing details about the error.
