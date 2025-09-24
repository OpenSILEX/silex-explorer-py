import requests
import pandas as pd
import os
from package.uri_name_manager.uri_name_table import getURIbyName, insert_into_uri_name
from package.exceptions.custom_exceptions import APIRequestError

def get_ls_os_types_by_exp(session, experiment_name, page_size=20, csv_filepath=None):
    """
    Retrieve all scientific object types for a given experiment using pagination and save to a CSV file.

    Args:
        session (dict): The authentication session, containing 'url_rest' and 'headers_rest'.
        experiment_name (str): The label of the experiment to filter the scientific object types.
        page_size (int): Number of items per page for pagination. Default is 20.
        csv_filepath(str): The filepath for the output CSV file.

    Returns:
        pd.DataFrame: A DataFrame containing the scientific object types' URIs and Names.

    Raises:
        APIRequestError: If the API request fails or returns an error.
    Example:
        >>> session = session
        >>> experiment_name = "ZA17"  # Replace with the actual experiment name
        >>> df = get_ls_os_types_by_exp(session, experiment_name, page_size=20)
        >>> print(df.head())
        # This will print the first few rows of the DataFrame containing scientific object types.
        # Additionally, the data will be saved to 'temp_files/scientific_object_types.csv'.

    """
    
    try:
        experiment_uri = getURIbyName(experiment_name)
    except ValueError as e:
        print(f"❌ {e}")
        exit(1)  # Stop execution due to the error 
        
    os_types_service_route = "/core/scientific_objects/used_types"

    url = f"{session['url_rest']}{os_types_service_route}"
    
    # Initialize pagination variables
    list_OS_types_by_experiment = []
    current_page = 0
    total_pages = 1  # Initial value to start the loop

    while current_page < total_pages:
        # Define parameters for the GET request
        params_get_os_types_by_experiment = {
            "experiment": experiment_uri,
            'pageSize': page_size,
            'page': current_page
        }
        
        try:
            # Send GET request with parameters
            response = requests.get(url, params=params_get_os_types_by_experiment, headers=session["headers_rest"])
            response.raise_for_status()
            
            # Parse JSON response
            json_response = response.json()
            results = json_response.get('result', [])
            
            # Append URIs to the list
            
            for result in results:
                list_OS_types_by_experiment.append({
                    'URI': result['uri'],
                    'Name': result['name']
                })
                
            # Update pagination info
            metadata = json_response.get('metadata', {}).get('pagination', {})
            total_pages = metadata.get('totalPages', 1)
            
            # Move to the next page
            current_page += 1
        
        except requests.exceptions.RequestException as e:
            # Raise a custom exception with a descriptive message
            raise APIRequestError(f"API request error: {str(e)}")
    
    # Save the list to a CSV file
    df = pd.DataFrame(list_OS_types_by_experiment)
    
    ## Save to CSV if requested
    if csv_filepath:
        if os.path.dirname(csv_filepath):  # Ensure the directory exists
            os.makedirs(os.path.dirname(csv_filepath), exist_ok=True)
        df.to_csv(csv_filepath, index=False)
        print(f"✅ Scientific object types have been saved to '{csv_filepath}'.")

    # Insert into global table if data exists
    if not df.empty:
        insert_into_uri_name(df)

    # Return the filtered experiments as a list
    return df
    
