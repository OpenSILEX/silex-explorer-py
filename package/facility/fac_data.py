import requests
from package.exceptions.custom_exceptions import APIRequestError
from package.uri_name_manager.uri_name_table import getURIbyName
import os
from collections import defaultdict
import pandas as pd
from package.facility.fac_var import get_variable_by_facility 
from datetime import datetime

def get_environmental_data_by_facility(session, facility_name, var_env=None,date_beginning=None, date_end=None, csv_filepath=None):
    """
    Retrieve environmental data for a facility and export it to CSV files organized by variables.

    Args:
        session (dict): Authentication session containing GraphQL endpoint and headers.
        facility_name (str): name of the facility (required).
        ls_var_env (pd.DataFrame, optional): List of environmental variables as a DataFrame. If None, variables are retrieved using `get_variable_by_facility`.
        date_beginning (str, optional): Start date in ISO format (YYYY-MM-DD). Defaults to the current date if not provided.
        date_end (str, optional): End date in ISO format (YYYY-MM-DD). Defaults to the current date if not provided.
        csv_filepath (str, optional): path for the generated CSV files.

    Returns:
        dict: A dictionary where keys are variable short names and values are DataFrames containing the environmental data.

    Raises:
        APIRequestError: If the GraphQL request fails or returns an error.
    Example:
        session = session
        facility_name = 'greenhouse'
        ls_var_env = default None
        date_beginning = '2023-01-01'
        date_end = '2023-01-31'
        data = get_environmental_data_by_facility(session, facility_uri, ls_var_env, date_beginning, date_end)
        
        # This will save data in CSV files and return the dictionary with DataFrames.
        # Example output: {'df_Temperature': DataFrame, 'df_Humidity': DataFrame}
    """
    try:
        facility_uri = getURIbyName(facility_name)
    except ValueError as e:
        print(f"❌ {e}")
        exit(1)  # Stop execution due to the error 
        
    # Get today's date in the format "YYYY-MM-DD"
    today = datetime.today().date()

    # If date_beginning or date_end are not provided, set them to today's date
    if date_beginning is None:
        date_beginning = today
        date_beginning = date_beginning.strftime("%Y-%m-%d")

    if date_end is None:
        date_end = today
        date_end = date_end.strftime("%Y-%m-%d")

    
    #Get the list of env variables of a facility
    ls_var_env=get_variable_by_facility(session, facility_name, date_beginning, date_end)
    if var_env is not None:
        # Filter the DataFrame to keep only the rows corresponding to the specified variables
        ls_var_env = ls_var_env[ls_var_env['Name'].isin(var_env)]
    
    # GraphQL query to fetch environmental data
    data_query = '''
    query GetEnvironmentalData($filter: FilterFindManyDataInput) {
      Data_findMany(filter: $filter) {
        target
        value
        variable
        date
        provenance {
            provWasAssociatedWith {
                uri
            }
        }
        prov_agent {
            agents {
                uri
            }
        }
      }
    }
    '''

    try:
        # Construct filter for GraphQL query/
        filter_input = {"target": facility_uri}
        # Add date conditions to _operators
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
        

        # Only include date filter if it contains valid conditions
        if date_filter:
            filter_input["_operators"] = {"date": date_filter}
    
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
        environmental_data = response_data.get("data", {}).get("Data_findMany", [])
        if not environmental_data:
            print("No environmental data found for these variables.")
            return []

        # Export the data to CSV using the provided export function
        dataframes=export_data_by_var_env_to_csv(ls_var_env, environmental_data, csv_filepath)
        print(f"Environmental data for facility : '{facility_name} successfully exported.")
        return dataframes

    except requests.exceptions.RequestException as e:
        raise APIRequestError(f"GraphQL request failed. Error: {str(e)}")

def export_data_by_var_env_to_csv(var_env, data, csv_filepath=None):
    """
    Export environmental data to CSV files organized by variable.

    Args:
        var_env (pd.DataFrame): DataFrame containing the environmental variables with columns 'URI' and 'Name'.
        data (list): List of dictionaries containing environmental data, each dictionary must have 'value', 'variable', and 'date'.
        csv_prefix (str, optional): Prefix for the generated CSV files. Defaults to 'Facility_'.

    Returns:
        dict: A dictionary where keys are variable names (short names) and values are DataFrames containing the data for each variable.

    Raises:
        ValueError: If the provided data or variables are empty or invalid.
    """
    
    if var_env is None or var_env.empty:
        print("Warning: No variables provided. Nothing to export.")
        return
    
    if not data:
        print("Warning: No data provided. Nothing to export.")
        return
    
    # Initialize a dictionary to store data by variable
    variable_data = defaultdict(list)

    # Construct a dictionary  URI -> Name
    uri_to_name = var_env.set_index('URI')['Name'].to_dict()
    
    # Get list of variable uris
    if 'URI' in var_env.columns:
        variables = var_env['URI'].dropna().tolist()
                
    # Iterate through the data and organize it by variable
    for item in data:
        # Extract device info from provenance or agent
        device_uris = []

        # Vérification dans 'provenance'
        if 'prov_agent' in item and isinstance(item['prov_agent'], dict):
                if 'agents' in item['prov_agent']:
                    agent_list = item['prov_agent']['agents']
                    for agent in agent_list:
                        device_uri = agent.get('uri', None)
                        if device_uri:
                            device_uris.append(device_uri)


        # Si 'provenance' est vide, vérifier dans 'prov_agent'
        if not device_uris:  # Si aucune donnée n'a été trouvée dans 'provenance'
            if 'provenance' in item and isinstance(item['provenance'], dict):
                if 'provWasAssociatedWith' in item['provenance']:
                    prov_list = item['provenance']['provWasAssociatedWith']
                    for prov in prov_list:
                        device_uri = prov.get('uri', None)
                        if device_uri:
                            device_uris.append(device_uri)
            
        # Si on a des URIs de devices, les joindre avec des virgules
        device_column_value = ', '.join(device_uris) if device_uris else ''

        if not variables or item['variable'] in variables:  # Check if the variable is in the provided list
            variable_data[item['variable']].append((item['value'], item['date'], device_column_value))

    
    if not variable_data:
            print("Warning: No data matched the variables provided.")
            return
        
    
    # Dictionary to store DataFrames
    dataframes = {}
    
    # For each unique variable, create a CSV file and write the corresponding data
    for variable, measurements in variable_data.items():
        
        # Get variable name from dictionnary else shortname
        variable_name = uri_to_name.get(variable, variable.split('/')[-1])

        # Build the DataFrame for this variable
        df = pd.DataFrame(measurements, columns=[variable_name, 'Date', 'Device'])

        # Add the DataFrame to the dictionary with its short name
        dataframes[f'df_{variable_name}'] = df
        
        if csv_filepath:
                os.makedirs(csv_filepath, exist_ok=True)  # Assure que le dossier existe
                csv_filename = os.path.join(csv_filepath, f'{variable_name}_data.csv')
                df.to_csv(csv_filename, index=False)
                print(f"✅ Data for variable '{variable_name}' has been saved to '{csv_filename}'.")
        
    
    return dataframes
        