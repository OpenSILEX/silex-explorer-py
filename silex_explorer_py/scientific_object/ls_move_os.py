import requests
import pandas as pd
from silex_explorer_py.exceptions.custom_exceptions import APIRequestError
from silex_explorer_py.uri_name_manager.uri_name_table import getURIbyName
from silex_explorer_py.experiment.ls_os_exp import get_experiment_id
import re
import os

def get_moves_by_os(session, os_name, experiment_name, date_beginning=None, date_end=None, csv_filepath=None):
    """
    Retrieve moves for a given scientific object and generate a CSV file.

    Args:
        session (dict): The authentication session containing GraphQL endpoint and headers.
        os_name (str): The label of the scientific object to filter moves.
        experiment (str): The experiment name to filter the scientific object.
        date_beginning (str, optional): The start date in ISO format (YYYY-MM-DD). Default is None.
        date_end (str, optional): The end date in ISO format (YYYY-MM-DD). Default is None.
        csv_filename (str, optional): The filename for the CSV output. Default is 'moves.csv'.

    Returns:
        list: A list of moves, where each move contains information about 'from', 'to', 'hasBeginning', and 'hasEnd'.

    Raises:
        APIRequestError: If the GraphQL request fails or returns an error.

    Example:
        session = session
        os_name = 'scientific_object_name'
        experiment = ['experiment_name']
        date_beginning = '2025-01-01'
        date_end = '2025-01-31'
        
        # Fetch moves for the given scientific object within the specified date range
        moves = get_moves_by_os(session, os_name, experiment, date_beginning, date_end)

        # The result will be a list of moves, e.g.:
        # [
        #     {'From': 'Location1', 'To': 'Location2', 'HasBeginning': '2025-01-01T12:00:00', 'HasEnd': '2025-01-01T13:00:00'},
        #     {'From': 'Location2', 'To': 'Location3', 'HasBeginning': '2025-01-02T12:00:00', 'HasEnd': '2025-01-02T13:00:00'}
        # ]
        # The CSV file will be saved in the 'temp_files' directory with the name based on the scientific object's label.
    """
   
    experiment=get_experiment_id(experiment_name, session)
 
    try:
        uri = getURIbyName(os_name)
    except ValueError as e:
        print(f"❌ {e}")
        exit(1)  # Stop execution due to the error
        
    # Check if the 'experiment' is a string
    if isinstance(experiment, str):
        # If it's a string, convert it into a list
        experiment = [experiment]
        
    # GraphQL query to retrieve the scientific object's label
    label_query = '''
    query GetScientificObjectLabel($uri: [ID], $experiment : [DataSource!]!) {
      ScientificObject(filter: {_id: $uri}, Experience: $experiment, inferred: true) {
        label
      }
    }
    '''
     # GraphQL query to retrieve moves
    moves_query = '''
    query GetMoves($uri: ID!, $dateBeginning: String, $dateEnd: String) {
      historique_positions(
        uri: $uri
        dateBeginning: $dateBeginning
        dateEnd: $dateEnd
      ) {
        from {
          label
        }
        to {
          label
        }
        hasBeginning {
          inXSDDateTimeStamp
        }
        hasEnd {
          inXSDDateTimeStamp
        }
      }
    }
    '''

    try:
        
        # Get the scientific object label
        label_response = requests.post(
            session["url_graphql"],
            json={'query': label_query, 'variables': {'uri': uri, "experiment": experiment}},
            headers=session["headers_graphql"]
        )
        label_response.raise_for_status()

        label_data = label_response.json()
        if 'errors' in label_data:
            error_message = label_data['errors'][0]['message']
            raise APIRequestError(f"Failed to retrieve scientific object label: {error_message}")

        scientific_object = label_data.get('data', {}).get('ScientificObject', [])
        if not scientific_object:
            raise APIRequestError(f"No scientific object found for URI: {uri}")
        label = scientific_object[0].get('label', 'unknown_object')

        # Create the CSV 
        safe_label = re.sub(r'[^a-zA-Z0-9_-]', '_', label)
        csv_filename = f"ls_moves_{safe_label}.csv"

        # Get the moves data
        moves_response = requests.post(
            session["url_graphql"],
            json={
                'query': moves_query,
                'variables': {'uri': uri, 'dateBeginning': date_beginning, 'dateEnd': date_end},
            },
            headers=session["headers_graphql"]
        )
        moves_response.raise_for_status()

        moves_data = moves_response.json()
        if 'errors' in moves_data:
            error_message = moves_data['errors'][0]['message']
            raise APIRequestError(f"Failed to retrieve moves: {error_message}")

        moves = moves_data.get('data', {}).get('historique_positions', [])

        if not moves:
            print("No moves found.")
            moves = []

        # Prepare data for CSV
        csv_data = []
        for move in moves:
            csv_data.append({
                'From': move.get('from', {}).get('label', '') if move.get('from') else '',
                'To': move.get('to', {}).get('label', '') if move.get('to') else '',
                'HasBeginning': move.get('hasBeginning', {}).get('inXSDDateTimeStamp', '') if move.get('hasBeginning') else '',
                'HasEnd': move.get('hasEnd', {}).get('inXSDDateTimeStamp', '') if move.get('hasEnd') else '',
            })

        # Convert to DataFrame and save as CSV
        df = pd.DataFrame(csv_data, columns=['From', 'To', 'HasBeginning', 'HasEnd'])
        
        # Save to CSV if requested
        if csv_filepath:
            if os.path.dirname(csv_filepath):  # Ensure the directory exists
                os.makedirs(os.path.dirname(csv_filepath), exist_ok=True)
            df.to_csv(csv_filepath, index=False)
            print(f"✅ Moves have been saved to '{csv_filepath}'.")

        return df

    except requests.exceptions.RequestException as e:
        raise APIRequestError(f"GraphQL request failed. Error: {str(e)}")
