import requests
from package.exceptions.custom_exceptions import APIRequestError
from tabulate import tabulate
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from package.experiment.ls_var_exp import get_ls_var_by_exp
from .data_exp_by_var import export_data_by_variable_to_csv

def fetch_chunk_data(chunk, experience, session):
    
    """Fetch data for a given chunk of OS URIs."""
    graphql_query = """
        query ScientificObject($experience: [DataSource!]!, $osUris: [ID]) {
            ScientificObject(
                inferred: true,
                Experience: $experience,
                filter: {""" + ("_id: $osUris" ) + """}
            ) {
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
        "osUris": chunk
    }

    response = requests.post(
        session["url_graphql"],
        json={'query': graphql_query, 'variables': variables},
        headers=session["headers_graphql"]
    )
    
    list_data_os = []
    if response.status_code == 200:
        scientific_objects = response.json().get('data', {}).get('ScientificObject', [])
        for obj in scientific_objects:
            if 'data' in obj and isinstance(obj['data'], list):
                list_data_os.extend(obj['data'])
    else:
        print(f"Error in chunk: {chunk}, status code: {response.status_code}, response: {response.text}")
        raise APIRequestError(f"Error: {response.status_code} - {response.text}")

    return list_data_os

def get_data_by_os_uri_variable(session, experience, experiment_uri, df_os, ls_var_exp=None ):
    """
    Retrieve data associated with scientific objects by experiment and object type.

    Args:
        graphql_endpoint (str): The GraphQL endpoint URL.
        headers_GraphQL (dict): HTTP headers for GraphQL requests, including authentication.
        experience (str): The URI of the experiment.
        obj_type (str): The URI of the object type.
        factor_level (list or None): Optional list of factor levels to filter the scientific objects.

    Returns:
        list: A list of dictionaries, each containing data points from the scientific objects.

    Raises:
        APIRequestError: If the API request fails.
    """
    
    # Maximum size of ids for each request
    max_ids_per_request = 40
    # List to store the results
    all_results = []

    # Check if the 'experiment' is a string
    if isinstance(experience, str):
        # If it's a string, convert it into a list
        experience = [experience]
        
    # Get the list of variables by experiment and save to CSV
    if ls_var_exp is None or ls_var_exp.empty:
        ls_var_exp= get_ls_var_by_exp(
                    session,
                    experiment_uri,
                    page_size=20,
                    csv_filename='variables.csv'
                )
    

    if 'uri' in df_os.columns:
        ls_os_uris = df_os['uri'].tolist()
    else:
        print("empty DataFrame.")
        return []
    
    dataFrames = {}
    
    # Divide the list of os_uris into several smaller sub-lists
    chunks = list(chunk_list(ls_os_uris, max_ids_per_request))
    j=0
    # Use ThreadPoolExecutor to fetch data in parallel
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_chunk = {executor.submit(fetch_chunk_data, chunk, experience, session): chunk for chunk in chunks}
        all_results_lock = Lock()
        for future in as_completed(future_to_chunk):
            chunk = future_to_chunk[future]
            try:
                j=j+1
                data = future.result()
                print(f'Results for chunk:{j}: {len(data)} items')  # Vérifiez la taille des résultats
                with all_results_lock:
                     all_results.extend(data)
                     print(f'Results: {len(all_results)} items')  # Vérifiez la taille des résultats

            except Exception as exc:
                print(f'Chunk {chunk} generated an exception: {exc}')
    
    
    dataFrames = export_data_by_variable_to_csv(ls_var_exp, all_results)
    return dataFrames
        
def chunk_list(data_list, chunk_size):
    """Divides a list into several sub-lists of size chunk_size."""
    for i in range(0, len(data_list), chunk_size):
        chunk = data_list[i:i + chunk_size]
        yield chunk
