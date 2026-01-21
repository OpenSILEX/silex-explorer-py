import pandas as pd
from silex_explorer_py.exceptions.custom_exceptions import APIRequestError
from silex_explorer_py.factor.ls_fl_factor import get_fl_by_factor
import os
from .ls_factor_exp import get_factors_by_exp


def get_fl_by_exp(session, experiment_uri, csv_filename='factor_levels.csv'):
    """
    Retrieve all factors and their levels for a given experiment, and export the data to a CSV file.

    Args:
        session (dict): The authentication session containing the GraphQL endpoint URL and headers.
        experiment_uri (str): The URI of the experiment for which factors and their levels need to be retrieved.
        csv_filename (str, optional): The name of the CSV file to store the retrieved factors and levels. Default is 'factor_levels.csv'.

    Returns:
        pandas.DataFrame: A DataFrame containing the factors, their URIs, and associated factor levels and their URIs.
    
    Raises:
        APIRequestError: If any GraphQL request fails, providing details on the error.

    Example:
        >>> session = session
        >>> experiment_uri = "https://example.com/experiment/123"
        >>> df = get_fl_by_exp(session, experiment_uri)
        >>> print(df.head())
        # Output:
        #   Factor           Factor URI                    Factor level          Factor level URI
        # 0 Factor 1       https://example.com/factor/1    Level 1               https://example.com/level/1
        # 1 Factor 1       https://example.com/factor/1    Level 2               https://example.com/level/2
        # 2 Factor 2       https://example.com/factor/2    Level 1               https://example.com/level/3
    """
    
    try:
        # Get the list of factors for the experiment
        factors = get_factors_by_exp(session, experiment_uri)
        
        factor_levels = []
        
        # For each factor, get the associated levels
        for factor in factors:
            factor_id = factor['uri']
            fl_by_factor = get_fl_by_factor(session, factor_id)
            
            for level in fl_by_factor:
                factor_levels.append({
                    'Factor': factor['label'],
                    'Factor URI': factor['uri'],
                    'Factor level': level['label'],
                    'Factor level URI': level['_id']
                })
        
        # Save the data to a CSV file
        df = pd.DataFrame(factor_levels)
        # Define the path to the temp_files directory
        project_root = os.path.dirname(os.path.abspath(__file__))  # Get directory of the current file
        while not os.path.exists(os.path.join(project_root, "temp_files")):  # Traverse upward until 'temp_files' is found
            project_root = os.path.dirname(project_root)

        # Path to the temp_files directory
        temp_dir = os.path.join(project_root, "temp_files")

        # Ensure the directory exists
        os.makedirs(temp_dir, exist_ok=True)

        # Full path for the file
        csv_path = os.path.join(temp_dir, csv_filename)

        # Save the filtered data to a CSV file
        df.to_csv(csv_path, index=False)
        print(f"Factor and factor levels has been saved to '{csv_path}'.")
        
        return df

    except APIRequestError as e:
        raise APIRequestError(f"Failed to retrieve factors and levels: {e}")

