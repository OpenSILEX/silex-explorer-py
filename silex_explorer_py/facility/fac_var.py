import requests
import pandas as pd
import os
from silex_explorer_py.exceptions.custom_exceptions import APIRequestError
from silex_explorer_py.uri_name_manager.uri_name_table import getURIbyName, insert_into_uri_name
import warnings

def get_variable_by_facility(session, facility_name, date_beginning=None, date_end=None, csv_filepath=None):
    """
    Retrieve detailed information for environmental variables linked to a facility within a date range.

    Args:
        session (dict): The authentication session containing GraphQL endpoint and headers.
        facility_name (str): The label of the facility to retrieve variable data for (required).
        date_beginning (str, optional): Start date for filtering data (format: YYYY-MM-DD). If not provided, defaults to the current date.
        date_end (str, optional): End date for filtering data (format: YYYY-MM-DD). If not provided, defaults to the current date.
        csv_filepath (str, optional): Filepath for the CSV output.

    Returns:
        pd.DataFrame: A DataFrame containing detailed variable information, including variable URI, name, entity, method, characteristic, and unit.

    Raises:
        APIRequestError: If any GraphQL request fails or returns an error.

    Example:
        session = session
        facility_uri = 'greenhouse'
        date_beginning = '2023-01-01'
        date_end = '2023-01-31'
        
        # Fetch variable details and save the result in a CSV file
        variable_data = get_variable_by_facility(session, facility_uri, date_beginning, date_end)

        # This will return a DataFrame like:
        #     URI                 | Name       | Entity    | Characteristic | Method | Unit
        # --------------------|------------|-----------|----------------|--------|-------
        # /variables/abc      | Temperature | Air    | Characteristic    | Method | °C
        # /variables/xyz      | Humidity    | Air    | Characteristic    | Method | %
        
        # The variable details will also be saved in 'variables.csv'
    """
    
    try:
        facility_uri = getURIbyName(facility_name)
    except ValueError as e:
        print(f"❌ {e}")
        exit(1)  # Stop execution due to the error 
        
    data_query = '''
    query GetEnvironmentalData($filter: FilterFindManyDataInput) {
      Data_findMany(filter: $filter) {
        variable
      }
    }
    '''

    try:
        # Step 1: Fetch unique variables based on facility and date range
        filter_input = {"target": facility_uri}
        date_filter = {}
        # Add date conditions to _operators
        if date_beginning and date_end and date_beginning == date_end:  # Both dates are equal and not None:  # Case where start and end date are the same
            # Set the range for the entire day
            date_filter["gte"] = f"{date_beginning}T00:00:00.000Z"
            date_filter["lte"] = f"{date_beginning}T23:59:59.999Z"
        else:
            if date_beginning:
                date_filter["gte"] = f"{date_beginning}T00:00:00.000Z" if "T" not in date_beginning else date_beginning
            if date_end:
                date_filter["lte"] = f"{date_end}T23:59:59.999Z" if "T" not in date_end else date_end        

        # Only include date filter if it contains valid conditions /
        if date_filter:
            filter_input["_operators"] = {"date": date_filter}
            
        response = requests.post(
            session["url_graphql"],
            json={'query': data_query, 'variables': {'filter': filter_input}},
            headers=session["headers_graphql"]
        )
        response.raise_for_status()
        json_response = response.json()

        if 'errors' in json_response:
            error_message = json_response['errors'][0]['message']
            raise APIRequestError(f"Failed GraphQL request with error: {error_message}")

        data = json_response.get('data', {}).get('Data_findMany', [])
        unique_variables = list({item.get('variable', '') for item in data})

        if not unique_variables:
            print("No variables found for the given facility and date range.")
            return pd.DataFrame()  # Return an empty DataFrame

        # Step 2: Fetch detailed information for the variables
        variable_details = get_variable_details(session, unique_variables)

        # Step 3: Save results to a CSV and return as DataFrame
        df = pd.DataFrame(variable_details)
        
        # Save to CSV if requested
        if csv_filepath:
            if os.path.dirname(csv_filepath):  # Ensure the directory exists
                os.makedirs(os.path.dirname(csv_filepath), exist_ok=True)
            df.to_csv(csv_filepath, index=False)
            print(f"✅ Environnement variables for facility : '{facility_name} have been saved to '{csv_filepath}'.")

        # Insert into global table if data exists
        if not df.empty:
            insert_into_uri_name(df)
        

        return df

    except requests.exceptions.RequestException as e:
        raise APIRequestError(f"Failed GraphQL request. Error: {str(e)}")



def get_variable_details(session, variable_ids):
    """
    Fetch detailed information about a list of variables.

    Args:
        session: The authentication session.
        variable_ids (list): List of variable IDs.

    Returns:
        list: A list of dictionaries containing detailed variable information.

    Raises:
        APIRequestError: If the GraphQL request fails.
    """
    variable_details_query = '''
    query GetVariableDetails($filter: FilterVariable) {
      Variable(inferred: true, filter: $filter) {
        _id
        label
        hasEntity {
          label
        }
        hasCharacteristic {
          label
        }
        hasMethod {
          label
        }
        hasUnit {
          label
        }
      }
    }
    '''

    try:
        response = requests.post(
            session["url_graphql"],
            json={'query': variable_details_query, 'variables': {'filter': {'_id': variable_ids}}},
            headers=session["headers_graphql"]
        )
        response.raise_for_status()

        json_response = response.json()

        if 'errors' in json_response:
            error_message = json_response['errors'][0]['message']
            raise APIRequestError(f"Failed GraphQL request with error: {error_message}")

        variable_data = json_response.get('data', {}).get('Variable', [])
        return [
            {
                'URI': var.get('_id', ''),
                'Name': var.get('label', ''),
                'Entity': var.get('hasEntity', {}).get('label', '') if var.get('hasEntity') else '',
                'Characteristic': var.get('hasCharacteristic', {}).get('label', '') if var.get('hasCharacteristic') else '',
                'Method': var.get('hasMethod', {}).get('label', '') if var.get('hasMethod') else '',
                'Unit': var.get('hasUnit', {}).get('label', '') if var.get('hasUnit') else '',
            }
            for var in variable_data
        ]

    except requests.exceptions.RequestException as e:
        raise APIRequestError(f"Failed GraphQL request. Error: {str(e)}")
