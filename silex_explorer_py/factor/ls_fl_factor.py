import requests
from silex_explorer_py.exceptions.custom_exceptions import APIRequestError

def get_fl_by_factor(session, factor_id):
    """
    Retrieve a list of factor levels for a given factor using GraphQL.

    Args:
        session (dict): Authentication session containing GraphQL endpoint and headers.
        factor_id (str): The ID of the factor whose levels are to be retrieved.

    Returns:
        list: A list of factor levels with their IDs and labels. Each factor level is represented by a dictionary with '_id' and 'label' keys.

    Raises:
        APIRequestError: If the GraphQL request fails or returns an error.

    Example:
        session = session
        factor_id = 'factor12345'

        # Fetch factor levels for the given factor
        factor_levels = get_fl_by_factor(session, factor_id)

        # The result might look like:
        # [
        #     {'_id': 'level1', 'label': 'Low'},
        #     {'_id': 'level2', 'label': 'Medium'},
        #     {'_id': 'level3', 'label': 'High'}
        # ]
        # The list contains dictionaries with the level ID and its corresponding label.
    """

    query = '''
    query getFactorLevelsByFactor($factorId: [ID]) {
        FactorLevel(filter: {hasFactor: $factorId}) {
            _id
            label
        }
    }
    '''

    variables = {
        "factorId": factor_id
    }

    try:
        response = requests.post(session["url_graphql"], json={'query': query, 'variables': variables}, headers=session["headers_graphql"])
        
        json_response = response.json()
        if 'errors' in json_response:
            error_message = json_response['errors'][0]['message']
            raise APIRequestError(f"Failed GraphQL request with error: {error_message}")        
         
        return json_response.get('data', {}).get('FactorLevel', [])
     
    except requests.exceptions.RequestException as e:
        raise APIRequestError(f"Failed to retrieve factor levels by factor: {str(e)}")
 