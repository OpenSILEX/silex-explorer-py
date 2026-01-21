import requests
import pandas as pd
import os
from silex_explorer_py.exceptions.custom_exceptions import APIRequestError
from collections import defaultdict
from silex_explorer_py.experiment.ls_var_exp import get_ls_var_by_exp
from silex_explorer_py.experiment.get_exp_id import get_experiment_id
from silex_explorer_py.uri_name_manager.uri_name_table import getURIbyName


def get_data_by_variable(session, experiment_name, obj_type_name, ls_var_exp=None, factor_level_uri=None, germplasm_uri=None, csv_filepath=None):
    
    """
    Retrieve data associated with scientific objects by experiment and object type, with optional filtering by factor levels and germplasm.

    Args:
        graphql_endpoint (str): The GraphQL endpoint URL.
        headers_GraphQL (dict): HTTP headers for GraphQL requests, including authentication.
        experience (str): The ID (name_dateBegin) of the experiment.
        experiment_uri (str): The URI of the experiment.
        obj_type (str): The URI of the object type.
        ls_var_exp (list): Optional list of variables of interest for the export (e.g., sensor readings, measurements).
        factor_level_uri (list or None): Optional list of factor level URIs to filter the scientific objects. Default is None.
        germplasm_uri (str or None): Optional URI for filtering based on specific germplasm (e.g., species or variety). Default is None.

    Returns:
    - dict: A dictionary where keys are variable names and values are DataFrames containing the data for each variable.

    Raises:
        APIRequestError: If the API request fails, providing details on the HTTP status code and error message.
    
    Description:
        This function first performs a GraphQL query to retrieve scientific objects of the specified type, associated with the
        given experiment. It applies optional filters for factor levels and germplasm. The function then extracts the target,
        value, and date data from each object and organizes them by variable. Finally, it exports the data for each variable into
        separate CSV files, where each CSV contains the measurements for one variable.
        
    Example:
    >>> session = session
    >>> experience = ["experiment_123_2023_01_01"]
    >>> experiment_uri = "https://example.com/experiment/123"
    >>> obj_type = "https://example.com/object_type/abc"
    >>> ls_var_exp = None  # or a DataFrame with specific variables
    >>> factor_level_uri = "https://example.com/factor_level/1"
    >>> germplasm_uri = "https://example.com/germplasm/variety1"
    >>> dataframes = get_data_by_variable(
    ...     session,
    ...     experience=experience,
    ...     experiment_uri=experiment_uri,
    ...     obj_type=obj_type,
    ...     ls_var_exp=ls_var_exp,
    ...     factor_level_uri=factor_level_uri,
    ...     germplasm_uri=germplasm_uri
    ... )
    >>> # Display data for each variable
    >>> for variable_name, df in dataframes.items():
    ...     print(f"Data for {variable_name}:")
    ...     print(df.head())  # Display first few rows of data for each variable
    """

    
    # Get object type URI 
    try:
        obj_type = getURIbyName(obj_type_name)
    except ValueError as e:
        print(f"❌ {e}")
        exit(1)  # Stop execution due to the error 
    
    # Get the list of variables by experiment and save to CSV
    if ls_var_exp is None or ls_var_exp.empty:
        ls_var_exp = get_ls_var_by_exp(session, experiment_name, page_size=20)
    
    # Get experiment id
    experience = get_experiment_id(experiment_name, session)

    # Check if the 'experience' is a string
    if isinstance(experience, str):
        experience = [experience]

    graphql_query = """
    query ScientificObject($experience: [DataSource!]!, $objType: String!""" + (", $factorLevel: [ID]" if factor_level_uri is not None else "")+ (", $germplasm: [ID]" if germplasm_uri is not None else "")  + """) {
        ScientificObject(
            inferred: true,
            Experience: $experience,
            filter: {type: $objType""" + (", hasFactorLevel: $factorLevel" if factor_level_uri is not None else "") +(", hasGermplasm: $germplasm" if germplasm_uri is not None else "")+ """}
        )  {
            data {
                target
                variable
                value
                date
            }
        }
    }
    """

    variables = {
        "experience": experience,
        "objType": obj_type,
    }

    if factor_level_uri is not None:
        variables["factorLevel"] = factor_level_uri
        
    if germplasm_uri is not None:
        variables["germplasm"] = germplasm_uri

    response = requests.post(
        session["url_graphql"],
        json={'query': graphql_query, 'variables': variables},
        headers=session["headers_graphql"]
    )
    list_data_os=[]
    if response.status_code == 200:
        scientific_objects = response.json().get('data', {}).get('ScientificObject', [])
        for obj in scientific_objects:
            if isinstance(obj['data'], list):
                list_data_os.extend(obj['data'])
     
        dataframes=export_data_by_variable_to_csv(ls_var_exp, list_data_os,csv_filepath=csv_filepath)
        return dataframes
    else:
        raise APIRequestError(f"Erreur: {response.status_code} - {response.text}")


    
def export_data_by_variable_to_csv(var_exp, data, csv_filepath=None):
    """
    Export data to CSV files organized by variable.

    Args:
    - variables (list): List of variables.
    - data (list): List of dictionaries containing data.
    - csv_prefix (str): Prefix for the CSV file names.

    Returns:
    - dict: A dictionary where keys are variable names and values are DataFrames.
    
    """
    
    if var_exp is None or var_exp.empty:
        print("Warning: No variables provided. Nothing to export.")
        return
    
    if not data:
        print("Warning: No data provided. Nothing to export.")
        return
    
    # Initialize a dictionary to store data by variable
    variable_data = defaultdict(list)

    # Construct a dictionary  URI -> Name
    uri_to_name = var_exp.set_index('URI')['Name'].to_dict()
    
    # Get list of variable uris
    if 'URI' in var_exp.columns:
        variables = var_exp['URI'].dropna().tolist()
                
    # Iterate through the data and organize it by variable
    for item in data:
        
        if not variables or item['variable'] in variables:  # Check if the variable is in the provided list
            variable_data[item['variable']].append((item['target'], item['value'], item['date']))

    
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
        df = pd.DataFrame(measurements, columns=['URI', variable_name, 'Date'])

        # Add the DataFrame to the dictionary with its short name
        dataframes[f'df_{variable_name}'] = df
        
        if csv_filepath:
                os.makedirs(csv_filepath, exist_ok=True)  # Assure que le dossier existe
                csv_filename = os.path.join(csv_filepath, f'{variable_name}_data.csv')
                df.to_csv(csv_filename, index=False)
                print(f"✅ Data for variable '{variable_name}' has been saved to '{csv_filename}'.")
    
    return dataframes
        