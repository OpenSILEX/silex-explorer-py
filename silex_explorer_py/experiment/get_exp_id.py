from silex_explorer_py.uri_name_manager.uri_name_table import getURIbyName
import requests
from datetime import datetime

def get_experiment_id(experiment_name, session):
    try:
        experiment_uri = getURIbyName(experiment_name)
    except ValueError as e:
        print(f"❌ {e}")
        exit(1)  # Stop execution due to the error

    graphql_query = '''
    query MyQuery($id: [ID]) {
      Experiment(filter: {_id: $id}) {
        label
        startDate
      }
    }
    '''

    try:
        response = requests.post(
            session["url_graphql"],
            json={'query': graphql_query, 'variables': {'id': experiment_uri}},
            headers=session["headers_graphql"]
        )
        response.raise_for_status()
        json_response = response.json()

        if 'errors' in json_response:
            error_message = json_response['errors'][0]['message']
            raise Exception(f"Failed GraphQL request with error: {error_message}")

        experiment_data = json_response.get('data', {}).get('Experiment', [])
        
        if not experiment_data:
            print("❌ No experiment found")
            exit(1)

        obj = experiment_data[0]
        label = obj.get('label', 'Unknown')
        label = label.replace('-', '_')
        start_date = obj.get('startDate', '')
        
        def parse_date(date_str):
            for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%d"):
                try:
                    return datetime.strptime(date_str, fmt).strftime("%Y_%m_%d")
                except ValueError:
                    continue
            raise ValueError(f"Unsupported date format: {date_str}")

        formatted_date = parse_date(start_date) if start_date else "Unknown_Date"
        return f"EXP_{label}_{formatted_date}"

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        exit(1)
