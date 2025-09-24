import requests
import pandas as pd
from package.exceptions.custom_exceptions import APIRequestError
from package.uri_name_manager.uri_name_table import getURIbyName
import os

def get_data_by_device(
    session, device_name, date_beginning=None, date_end=None,  csv_filepath=None):
    """
    Retrieve measured data for a given device and optionally generate a CSV file.
    Args:
        session: The authentication session.
        device_name (str): The label of the device to filter data.
        date_beginning (str, optional): The start date in ISO format (YYYY-MM-DD).
        date_end (str, optional): The end date in ISO format (YYYY-MM-DD).
        csv_filepath (str, optional): The full file path (including filename) for the CSV output.
                                      If not provided, the data will not be saved to a file.
    Returns:
        pd.DataFrame: A DataFrame containing the measured data with columns:
            - "Device URI": URI of the device.
            - "Target": The target of the measured data.
            - "Value": The value of the measured data.
            - "Variable": The variable associated with the measured data.
            - "Date": The date of the measurement.

    Raises:
        APIRequestError: If the GraphQL request fails.

    Example:
        Retrieve data for a device and save it as a CSV:

        >>> df = get_data_by_device(
        ...     session=session,
        ...     device_name="aria_hr1_p",
        ...     date_beginning="2023-01-01",
        ...     date_end="2023-01-31",
        ...     csv_filepath="path/to/save/output.csv"        ... )
        >>> print(df.head())
        
        For more examples, see the file `examples/get_data_by_device.py`.  
    """
    try:
        device_uri = getURIbyName(device_name)
    except ValueError as e:
        print(f"❌ {e}")
        exit(1)  # Stop execution due to the error 
    
    # GraphQL query to retrieve measured data
    data_query = '''
    query GetMeasuredData($filter: FilterFindManyDataInput) {
      Data_findMany(filter: $filter) {
        target
        value
        variable
        date
      }
    }
    '''

    try:
        # Construct filter for GraphQL query
        filter_input = {"provenance": {"provWasAssociatedWith": {"uri": device_uri}}}

        # Add date filters only if provided
        if date_beginning or date_end:
            filter_input["_operators"] = {}
            if date_beginning:
                filter_input["_operators"]["date"] = {"gte": date_beginning}
            if date_end:
                filter_input["_operators"]["date"] = filter_input["_operators"].get("date", {})
                filter_input["_operators"]["date"]["lte"] = date_end

        # Execute the query
        response = requests.post(
            session["url_graphql"],
            json={"query": data_query, "variables": {"filter": filter_input}},
            headers=session["headers_graphql"]
        )
        response.raise_for_status()

        # Parse the JSON response
        response_data = response.json()
        if "errors" in response_data:
            error_message = response_data["errors"][0]["message"]
            raise APIRequestError(f"GraphQL query failed: {error_message}")

        # Extract the data
        measured_data = response_data.get("data", {}).get("Data_findMany", [])
        if not measured_data:
            print("No measured data found.")
            return []

        # Prepare data for CSV
        csv_data = [
            {
                "URI": device_uri,
                "Target": item.get("target", ""),
                "Value": item.get("value", ""),
                "Variable": item.get("variable", ""),
                "Date": item.get("date", ""),
            }
            for item in measured_data
        ]

        # Convert to DataFrame and save as CSV
        df = pd.DataFrame(csv_data, columns=["URI", "Target", "Value", "Variable", "Date"])
        
        
        if csv_filepath:
            if os.path.dirname(csv_filepath):  # Ensure the directory exists
                os.makedirs(os.path.dirname(csv_filepath), exist_ok=True)
            df.to_csv(csv_filepath, index=False)
            print(f"✅ Measured data on device has been saved to :'{csv_filepath}'.")
        
        return df

    except requests.exceptions.RequestException as e:
        raise APIRequestError(f"GraphQL request failed. Error: {str(e)}")

