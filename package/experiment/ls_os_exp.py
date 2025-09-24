import requests
import pandas as pd
from package.exceptions.custom_exceptions import APIRequestError
from package.uri_name_manager.uri_name_table import getURIbyName, insert_into_uri_name
from package.experiment.get_exp_id import get_experiment_id
import os

def get_os_by_exp(session, experiment_name, obj_type_name, factor_level_uri=None, germplasm_uri=None, factor_levels=None, germplasm_type=None, germplasm_name=None, csv_filepath=None):
    """
    Retrieve scientific objects and their associated details by experiment and object type, 
    with optional dynamic filtering for factor levels and germplasm.

    Args:
        session (dict): Authentication session with GraphQL endpoint and headers.
        experiment_name (str): Name of the experiment, used to filter objects.
        obj_type_name (str): Name of the object type to filter.
        factor_level_uri (str, optional): Factor level URI to filter objects. Default is None.
        germplasm_uri (str, optional): Germplasm URI to filter objects. Default is None.
        factor_levels (list, optional): List of factor levels in the format 'factor.factorlevel' to filter objects. Default is None.
        germplasm_type (str, optional): Type of germplasm to filter by. Default is None.
        germplasm_name (str, optional): Name of germplasm to filter by. Default is None.
        csv_filepath (str, optional): path of the CSV file to save the resulting data.

    Returns:
        pd.DataFrame: A DataFrame containing detailed information about the scientific objects.

    Raises:
        APIRequestError: If the API request fails or returns an error.

    Example:
        >>> session = session
        >>> experiment_name = "experiment_name"
        >>> obj_type = "plant"
        >>> df = get_os_by_exp(session, experiment_name, obj_type_name, factor_levels=["Factor1.Level1"], germplasm_type="Variety", germplasm_name="GermplasmName")
        >>> print(df.head())
    """
    
    # Get object type URI 
    try:
        obj_type = getURIbyName(obj_type_name)
    except ValueError as e:
        print(f"❌ {e}")
        exit(1)  # Stop execution due to the error 
    
    # Get experiment id
    experience=get_experiment_id(experiment_name, session)
  
    # Check if the 'experiment' is a string
    if isinstance(experience, str):
        # If it's a string, convert it into a list
        experience = [experience]
        
    # Base GraphQL query with placeholders for dynamic filtering
    graphql_query = '''
    query ScientificObject($experience: [DataSource], $filter: FilterScientificObject) {
        ScientificObject(Experience: $experience, filter: $filter, inferred: true) {
            _id
            label
            _type
            hasFactorLevel {
                label
                hasFactor {
                    label
                }
            }
            hasGermplasm {
                fromSpecies {
                    _id
                    label
                }
                fromVariety {
                    _id
                    label
                }
                fromAccession {
                    _id
                    label
                }
                label
                type
                _type(inferred: true)
            }
        }
    }
    '''

    # Constructing the filter dynamically (for obj_type, factor_level, and germplasm)
    filter_input = {"type": obj_type}
    if factor_level_uri:
        filter_input["hasFactorLevel"] = factor_level_uri
    if germplasm_uri:
        filter_input["hasGermplasm"] = germplasm_uri

    try:
        # Execute the GraphQL request
        response = requests.post(
            session["url_graphql"],
            json={'query': graphql_query, 'variables': {'experience': experience, 'filter': filter_input}},
            headers=session["headers_graphql"]
        )
        response.raise_for_status()

        # Process the response
        json_response = response.json()
        if 'errors' in json_response:
            error_message = json_response['errors'][0]['message']
            raise APIRequestError(f"Failed GraphQL request with error: {error_message}")

        scientific_objects = json_response.get('data', {}).get('ScientificObject', [])
        list_scientific_objects = []

        # Parsing and structuring the scientific objects data
        for obj in scientific_objects:
            row = {
                'URI': obj['_id'],
                'Name': obj['label'],
                'type': obj['_type'][0] if obj['_type'] else None,
            }

            # Handling factor levels
            if obj.get('hasFactorLevel'):
                for factor_level in obj['hasFactorLevel']:
                    factor_name = factor_level['hasFactor'][0]['label']
                    factor_level_label = factor_level['label']
                    row[factor_name] = row.get(factor_name, '') + (', ' if row.get(factor_name) else '') + factor_level_label

            # Handling germplasm data
            if obj.get('hasGermplasm'):
                for idx, germplasm in enumerate(obj['hasGermplasm'], start=1):
                    row[f'Germplasm_type_{idx}'] = germplasm.get('_type', [None])[0]
                    row[f'Germplasm_{idx}'] = germplasm['label']

                    if germplasm.get('fromSpecies'):
                        row[f'Species_{idx}'] = ', '.join(species['label'] for species in germplasm['fromSpecies'])
                    if germplasm.get('fromVariety'):
                        row[f'Variety_{idx}'] = ', '.join(variety['label'] for variety in germplasm['fromVariety'])
                    if germplasm.get('fromAccession'):
                        row[f'Accession_{idx}'] = ', '.join(accession['label'] for accession in germplasm['fromAccession'])

            list_scientific_objects.append(row)

        # Convert to DataFrame and clean up
        df = pd.DataFrame(list_scientific_objects)
         
        # If a specific factor is provided, filter the DataFrame to include only rows
        # where the factor column matches the specified factor level
        # If a list of 'factor.factorlevel' strings is provided, apply the filter for each element
        if factor_levels is not None:
            for factor_level_str in factor_levels:
                # Split the 'factor.factorlevel' string into two parts: factor and factor level
                factor, factor_level = factor_level_str.split('.')
                
                # Check if the factor column exists in the DataFrame
                if factor in df.columns:
                    # Filter the DataFrame based on the factor level, checking if the level is present in the corresponding column
                    df = df[df[factor].apply(lambda x: isinstance(x, str) and factor_level in x.split(','))]
                else:
                    # If the factor does not exist in the columns, log a warning or skip the filter
                    print(f"Warning: Factor '{factor}' not found in the DataFrame columns. Skipping this filter.")
                    
        # Apply germplasm type filter
        # Check if germplasm_type is provided
        if germplasm_type is not None:
            # Step 1: If germplasm_name is provided, filter by both germplasm_type and germplasm_name
            if germplasm_name is not None:
                # Filter columns that start with 'Germplasm_' or match the germplasm_type
                name_columns = [col for col in df.columns if col.startswith('Germplasm_') or col.startswith(germplasm_type)]
                if name_columns:
                    # Create a condition to check if germplasm_name exists in any of these columns
                    name_filter = df[name_columns].apply(
                        lambda row: germplasm_name in row.values, axis=1
                    )
                    df = df[name_filter]  # Apply the filter based on germplasm_name
            
            # Step 2: If germplasm_name is not provided, filter only by Germplasm_type columns
            else:
                # Filter the DataFrame based on columns starting with 'Germplasm_type'
                type_filter = df[[col for col in df.columns if col.startswith('Germplasm_type')]].apply(
                    lambda row: germplasm_type in row.values, axis=1
                )
                df = df[type_filter]  # Apply the filter based on Germplasm_type
        # Remove columns that contain only missing values (NaN) from the DataFrame
        df = df.copy()  
        df.dropna(axis=1, how='all', inplace=True)

        # Save to CSV if requested
        if csv_filepath:
            if os.path.dirname(csv_filepath):  # Ensure the directory exists
                os.makedirs(os.path.dirname(csv_filepath), exist_ok=True)
            df.to_csv(csv_filepath, index=False)
            print(f"✅  Scientific objects have been saved to '{csv_filepath}'.")

        # Insert into global table if data exists
        if not df.empty:
            insert_into_uri_name(df)
        
        return df

    except requests.exceptions.RequestException as e:
        raise APIRequestError(f"Failed GraphQL request. Error: {str(e)}")


