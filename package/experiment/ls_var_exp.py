import requests
import pandas as pd
import os
from package.exceptions.custom_exceptions import APIRequestError
from package.uri_name_manager.uri_name_table import getURIbyName, insert_into_uri_name


def get_ls_var_by_exp(session,experiment_name, page_size=20, csv_filepath=None):
    """
    Retrieve all variables for a given experiment using pagination.

    Args:
        session (dict): The authentication session with the API endpoint and headers.
        experiment_uri (str): URI of the experiment to retrieve variables for.
        page_size (int): Number of items per page for pagination. Default is 20.
        csv_filename (str): Filename for the output CSV file. Default is 'variables.csv'.

    Returns:
        pd.DataFrame: A DataFrame containing variables and their associated details for the experiment.
    
    Raises:
        APIRequestError: If the API request fails.

    Example:
        >>> session = session
        >>> experiment_uri = "https://example.com/experiment/123"  # Replace with the actual experiment URI
        >>> df = get_ls_var_by_exp(session, experiment_uri, page_size=20, csv_filename='variables.csv')
        >>> print(df.head())
        # This will print the first few rows of the DataFrame containing variables for the experiment.
        # Additionally, the data will be saved to 'temp_files/variables.csv'.
    """
    
    # Get experiment URI from table uri_name
    try:
        experiment_uri = getURIbyName(experiment_name)
    except ValueError as e:
        print(f"❌ {e}")
        exit(1)  # Stop execution due to the error 
      
      
    variables_service_route = "/core/variables"
    
    url = f"{session['url_rest']}{variables_service_route}"
    
    list_variables_by_experiment = []
    current_page = 0
    has_next_page = True
    with_associated_data = True
    
    while has_next_page:
        # Construct parameters for the GET request
        params = {
            "withAssociatedData": str(with_associated_data).lower(),
            "experiments": experiment_uri,
            "page": current_page,
            "pageSize": page_size
        }
        
        try: 
            # Send a GET request with the parameters
            response = requests.get(url, params=params, headers=session["headers_rest"])
            
            json_response = response.json()
            results = json_response.get('result', [])
            
            for result in results:
                list_variables_by_experiment.append({
                    "URI": result["uri"],
                    "Name": result["name"],
                    "entity_name": result["entity"]["name"],
                    "characteristic_name": result["characteristic"]["name"],
                    "method_name": result["method"]["name"],
                    "unit_name": result["unit"]["name"]
                })
            # Update pagination info
            metadata = json_response.get('metadata', {}).get('pagination', {})
            has_next_page = metadata.get('hasNextPage', False)
            
            # Move to the next page
            current_page += 1
        
        except requests.exceptions.RequestException as e:
            raise APIRequestError(f"API request error: {str(e)}")
    
    
    # Save the extracted data to a CSV file
    df = pd.DataFrame(list_variables_by_experiment)
    # Save to CSV if requested
    if csv_filepath:
        if os.path.dirname(csv_filepath):  # Ensure the directory exists
            os.makedirs(os.path.dirname(csv_filepath), exist_ok=True)
            
        df.to_csv(csv_filepath, index=False)
        print(f"✅ Variables for experiment : '{experiment_name}' have been saved to '{csv_filepath}'.")
     
    # Insert into global table if data exists
        if not df.empty:
            insert_into_uri_name(df)
        
    return df

