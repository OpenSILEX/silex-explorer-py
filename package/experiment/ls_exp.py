import requests
import pandas as pd
from package.exceptions.custom_exceptions import APIRequestError
from package.uri_name_manager.uri_name_table import insert_into_uri_name
import os
from datetime import datetime

def get_ls_exp(session, species_uri=None, project_uri=None, active_date=None, 
               species_name=None, project_name=None,   csv_filepath=None):
    """
    Retrieve a list of experiments using GraphQL with optional filtering by space uri, project uri, specific date, species name, and project name.

    Args:
        session (dict): The authentication session.
        species_uri (str, optional): URI of the species to filter experiments. Default is None.
        project_uri (str, optional): URI of the project to filter experiments. Default is None.
        active_date (str, optional): Specific date to check active experiments in 'YYYY-MM-DD' format. Default is None.
        species_name (str, optional): Name of the species to filter experiments. Default is None.
        project_name (str, optional): Name of the project to filter experiments. Default is None.
        csv_filepath (str): pathof the CSV file to save the resulting experiments data. Default is 'list_experiments.csv'.

    Returns:
        pd.DataFrame: A DataFrame containing the experiments that match the filtering criteria, including:
            - "_id": ID of the experiment.
            - "label": The label of the experiment.
            - "startDate": Start date of the experiment.
            - "endDate": End date of the experiment.
            - "hasSpecies": The species associated with the experiment.
            - "hasProject": The project associated with the experiment.

    Description:
        This function retrieves a list of experiments from the server using a GraphQL query, with optional filters applied for
        space, project, species, and active_date. The filters are not required to be used together and can be applied individually.
        The function then flattens the species and project information for better readability and finally exports the filtered data into a CSV file for further analysis.

    Example:
        >>> df = get_ls_exp(
        ...     session=session,
        ...     space_uri="http://example.com/space/123",
        ...     project_uri="http://example.com/project/456",
        ...     active_date="2023-01-01",
        ...     species_name="Arabidopsis",
        ...     project_name="Plant Research",
        ... )
        >>> print(df.head())
    """
    # GraphQL query with optional filters
    query = '''
    query list_experiments($filter: FilterExperiment) {
        Experiment(filter: $filter) {
            _id
            label
            startDate
            endDate
            hasSpecies {
                label
            }
            hasProject {
                label
            }
        }
    }
    '''

    # Construct filter dynamically
    filter_input = {}
    if species_uri:
        filter_input["hasSpecies"] = species_uri
    if project_uri:
        filter_input["hasProject"] = project_uri

    try:
        # Make the GraphQL request
        response = requests.post(
            session["url_graphql"],
            json={'query': query, 'variables': {'filter': filter_input}},
            headers=session["headers_graphql"]
        )
        response.raise_for_status()

        json_response = response.json()
        if 'errors' in json_response:
            error_message = json_response['errors'][0]['message']
            raise APIRequestError(f"Failed GraphQL request with error: {error_message}")

        list_experiments = json_response.get('data', {}).get('Experiment', [])

        # Flatten species and project information for better readability
        for experiment in list_experiments:
            experiment['hasSpecies'] = ', '.join(species.get('label', '') for species in experiment.get('hasSpecies', []))
            experiment['hasProject'] = ', '.join(project.get('label', '') for project in experiment.get('hasProject', []))

        # Convert the list to a DataFrame
        df = pd.DataFrame(list_experiments)
        df.rename(columns={"_id": "URI", "label": "Name"}, inplace=True)
        
        # Filter by date
        if active_date:
            date_obj = datetime.strptime(active_date, '%Y-%m-%d')
            df['startDate'] = pd.to_datetime(df['startDate'], errors='coerce')
            df['endDate'] = pd.to_datetime(df['endDate'], errors='coerce')
            df = df[(df['startDate'] <= date_obj) & (df['endDate'] >= date_obj)]

        # Filter by species name and project name
        if species_name:
            df = df[df['hasSpecies'].str.contains(species_name, case=False, na=False)]
        if project_name:
            df = df[df['hasProject'].str.contains(project_name, case=False, na=False)]

        # Save to CSV if requested
        if csv_filepath:
            if os.path.dirname(csv_filepath):  # Ensure the directory exists
                os.makedirs(os.path.dirname(csv_filepath), exist_ok=True)
            df.to_csv(csv_filepath, index=False)
            print(f"✅ Experiments has been saved to '{csv_filepath}'.")

        # Insert into global table if data exists
        if not df.empty:
            insert_into_uri_name(df)
        return df

    except requests.exceptions.RequestException as e:
        raise APIRequestError(f"Failed GraphQL request. Error: {str(e)}")
