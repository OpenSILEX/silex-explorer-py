import requests

from ..exceptions import APIRequestError
from ..uri_name_manager.uri_name_table import getURIbyName
from .get_exp_id import get_experiment_id
from .ls_var_exp import get_ls_var_by_exp
from .export_data import export_data_by_variable_to_csv


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

