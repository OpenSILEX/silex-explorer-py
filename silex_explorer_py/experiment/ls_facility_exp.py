import requests
import pandas as pd
from silex_explorer_py.exceptions.custom_exceptions import APIRequestError
from silex_explorer_py.uri_name_manager.uri_name_table import getURIbyName, insert_into_uri_name
import os
import warnings


def get_facilities_by_experiment(session, experiment_name,csv_filepath=None):
    """
    Retrieve facilities associated with a given experience using GraphQL query, 
    including type and geometry data, and save the results in a CSV file.

    Args:
        session (dict): Authentication session with GraphQL endpoint and headers.
        experience_name (str): The label of the experience for which facilities are to be retrieved.
        csv_filepath (str, optional): The path of the CSV file to save the resulting data. 

    Returns:
        pd.DataFrame: A DataFrame containing the details of the facilities associated with the experience.

    Raises:
        APIRequestError: If the API request fails or returns an error.

    Example:
        >>> session = session
        >>> experiment_name = "ZA17"
        >>> df = get_facilities_by_experience(session, experiment_name)
        >>> print(df.head())
    """
    
    try:
        experience_uri = getURIbyName(experiment_name)
    except ValueError as e:
        print(f"❌ {e}")
        exit(1)  # Stop execution due to the error 

    # Define the GraphQL query for fetching facilities associated with an experience
    graphql_query = '''
    query GetFacilities($experienceUri: [ID]) {
        Experiment(filter: {_id: $experienceUri}) {
            usesFacility {
                _id
                _type(inferred: true)
                geometry {
                    geometry {
                        type
                        coordinates
                    }
                }
                label
            }
        }
    }
    '''
    
    try:
        # Execute the GraphQL request/
        response = requests.post(
            session["url_graphql"],
            json={'query': graphql_query, 'variables': {'experienceUri': experience_uri}},
            headers=session["headers_graphql"]
        )
        response.raise_for_status()

        # Process the response
        json_response = response.json()
        if 'errors' in json_response:
            error_message = json_response['errors'][0]['message']
            raise APIRequestError(f"Failed GraphQL request with error: {error_message}")

        facilities = json_response.get('data', {}).get('Experiment', [{}])[0].get('usesFacility', [])
        list_facilities = []

        # Parsing and structuring the facility data
        for facility in facilities:
            row = {
                'URI': facility['_id'],
                'Name': facility['label'],
                'Type': facility['_type'][0] if facility['_type'] else None,
            }

            # Handling the geometry data
            # Handling geometry
            if facility.get('geometry'):
                for geo in facility['geometry']:
                    geo_type = geo['geometry']['type']
                    coordinates = geo['geometry']['coordinates']
                    row['geometry'] = f'{geo_type}({", ".join(map(str, coordinates))})'
            
            list_facilities.append(row)

        # Convert to DataFrame
        df = pd.DataFrame(list_facilities)

        # Remove columns that contain only missing values (NaN) from the DataFrame
        df.dropna(axis=1, how='all', inplace=True)

        # Save to CSV if requested
        if csv_filepath:
            if os.path.dirname(csv_filepath):  # Ensure the directory exists
                os.makedirs(os.path.dirname(csv_filepath), exist_ok=True)
            df.to_csv(csv_filepath, index=False)
            print(f"✅ Facilities has been saved to '{csv_filepath}'.")

        # Insert into global table if data exists
        if not df.empty:
            insert_into_uri_name(df)
        return df

    except requests.exceptions.RequestException as e:
        raise APIRequestError(f"Failed GraphQL request. Error: {str(e)}")
