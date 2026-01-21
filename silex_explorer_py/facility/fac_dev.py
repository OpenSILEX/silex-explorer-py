import requests
import os
import pandas as pd
from silex_explorer_py.exceptions.custom_exceptions import APIRequestError
from silex_explorer_py.uri_name_manager.uri_name_table import getURIbyName, insert_into_uri_name


def get_devices_by_facility(session, facility_name, page_size=20, csv_filepath=None):
    """
    Retrieve all devices associated with a given facility using pagination.

    Args:
        session (dict): The authentication session containing REST API endpoint and headers.
        facility_name (str): name of the facility to retrieve devices for.
        page_size (int, optional): Number of items per page for pagination. Default is 20.
        csv_filename (str, optional): Filename for the output CSV file. Default is 'devices.csv'.

    Returns:
        list: A list of dictionaries where each dictionary represents a device with 'uri', 'type', and 'name'.

    Raises:
        APIRequestError: If the API request fails or returns an error.
    Example:
        session = session
        facility_name = '/facilities/12345'
        devices = get_devices_by_facility(session,facility_name)
        
        # This will retrieve device data associated with the facility and return a list like:
        # [{'uri': '/devices/1', 'type': 'Sensor', 'name': 'Temperature Sensor'},
        #  {'uri': '/devices/2', 'type': 'Sensor', 'name': 'Humidity Sensor'}]
    """
    try:
        facility_uri = getURIbyName(facility_name)
    except ValueError as e:
        print(f"❌ {e}")
        exit(1)  # Stop execution due to the error 
        
    devices_service_route = "/core/devices"
    url = f"{session['url_rest']}{devices_service_route}"
    
    list_devices = []
    current_page = 0
    has_next_page = True

    while has_next_page:
        # Construct parameters for the GET request
        params = {
            "facility": facility_uri,
            "page": current_page,
            "pageSize": page_size
        }
        
        try:
            # Send a GET request with the parameters
            response = requests.get(url, params=params, headers=session["headers_rest"])
            response.raise_for_status()  # Raise an HTTPError if the response code is 4xx/5xx
            
            json_response = response.json()
            results = json_response.get('result', [])
            
            for result in results:
                list_devices.append({
                    "URI": result["uri"],
                    "type": result["rdf_type_name"],
                    "Name": result["name"]
                })
            
            # Update pagination info
            metadata = json_response.get('metadata', {}).get('pagination', {})
            has_next_page = metadata.get('hasNextPage', False)
            
            # Move to the next page
            current_page += 1
        
        except requests.exceptions.RequestException as e:
            raise APIRequestError(f"API request error: {str(e)}")
    
    # Save the extracted data to a CSV file
    df = pd.DataFrame(list_devices)
    # Save to CSV if requested
    if csv_filepath:
        if os.path.dirname(csv_filepath):  # Ensure the directory exists
            os.makedirs(os.path.dirname(csv_filepath), exist_ok=True)
        df.to_csv(csv_filepath, index=False)
        print(f"✅ Devices has been saved to :'{csv_filepath}'.")

    # Insert into global table if data exists
    if not df.empty:
        insert_into_uri_name(df)
        
    return df
