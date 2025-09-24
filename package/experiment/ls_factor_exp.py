import requests
from package.exceptions.custom_exceptions import APIRequestError


def get_factors_by_exp(session, experiment_uri):
    """
    Retrieve a list of factors by experiment using GraphQL.

    Args:
        session (dict): The authentication session containing the GraphQL endpoint URL and headers.
        experiment_uri (str): The URI of the experiment for which factors need to be retrieved.

    Returns:
        list: A list of dictionaries, where each dictionary contains 'uri' and 'label' for each factor.

    Raises:
        APIRequestError: If the GraphQL request fails or returns an error.

    Example:
        >>> session = session
        >>> experiment_uri = "https://example.com/experiment/123"
        >>> factors = get_factors_by_exp(session, experiment_uri)
        >>> print(factors)
        [{'uri': 'https://example.com/factor/1', 'label': 'Factor 1'}, 
         {'uri': 'https://example.com/factor/2', 'label': 'Factor 2'}]
    """
    

    query = '''
    query getFactorsByExperiment($experimentUri: [ID]) {
        Experiment(filter: {_id: $experimentUri}) {
            studyEffectOf {
                _id
                label
            }
        }
    }
    '''

    # Variables for the query
    variables = {
        "experimentUri": experiment_uri
    }
    try:
        response = requests.post(session["url_graphql"], json={'query': query, 'variables': variables}, headers=session["headers_graphql"])
        
        json_response = response.json()
        if 'errors' in json_response:
            error_message = json_response['errors'][0]['message']
            raise APIRequestError(f"Failed GraphQL request with error: {error_message}")        
        
        
        experiment_data = json_response.get('data', {}).get('Experiment', [])
        
        factors = [{'uri': factor['_id'], 'label': factor['label'].strip()} for exp in experiment_data for factor in exp.get('studyEffectOf', [])]

        return factors
        
    except requests.exceptions.RequestException as e:
        raise APIRequestError(f"Failed to retrieve factors by experiment: {str(e)}")
    
