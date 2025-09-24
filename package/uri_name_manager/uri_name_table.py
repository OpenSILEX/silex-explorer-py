import os
import pandas as pd
import warnings

def init_uri_name(csv_path=None, save=False):
    """
    Initializes the global variable `uri_name_table`, and optionally saves it to a CSV file.

    - If `csv_path` is provided and the file exists, it loads the CSV file into `uri_name_table`.
    - If no path is provided or the file does not exist, it checks if a file named `uri_name.csv` exists in the current working directory.
      - If the file exists, it loads it into `uri_name_table`.
      - If the file does not exist, it creates an empty DataFrame with 'uri' and 'name' columns.
    - If `save` is True, it saves the `uri_name_table` to the specified `csv_path` or the default `uri_name.csv` in the current directory if no path is provided.

    Parameters:
    - csv_path (str, optional): Path to a CSV file containing 'uri' and 'name' columns.
    - save (bool, optional): If True, saves the `uri_name_table` to a csv.

    Returns:
    - pd.DataFrame: The global URI-Name table.
    """
    global uri_name_table  # Use the global variable
    
    if csv_path and os.path.exists(csv_path):
        # Load the provided CSV file into the DataFrame
        uri_name_table = pd.read_csv(csv_path)
        print(f"CSV file loaded: {csv_path}")
    elif os.path.exists("uri_name.csv"):
        # If no path is provided and the default file exists, load it
        uri_name_table = pd.read_csv("uri_name.csv")
        print("CSV file loaded: uri_name.csv from current directory.")
    else:
        # Create an empty DataFrame if no file exists
        uri_name_table = pd.DataFrame(columns=["URI", "Name"])
        print("Initialized an empty URI-Name table.")

    # If save is True, save the DataFrame to the provided file path or the default path
    if save:
        # If no CSV path is given, use the default 'uri_name.csv' in the current directory
        if not csv_path:
            csv_path = "uri_name.csv"
        uri_name_table.to_csv(csv_path, index=False)
        print(f"URI-Name table has been saved to: {csv_path}")

    return uri_name_table

def insert_into_uri_name(new_data):
    """
    Inserts multiple rows into the global uri_name_table.
    :param new_data: DataFrame containing 'URI' and 'Name' columns.
    """
    global uri_name_table  # Use the global variable
    if uri_name_table is None:
        raise ValueError("Error: The uri_name_table is not initialized. Call init_uri_name() first.")

    if not isinstance(new_data, pd.DataFrame) or not {"URI", "Name"}.issubset(new_data.columns):
        raise ValueError("Invalid input: new_data must be a DataFrame containing 'URI' and 'Name' columns.")

    new_data = new_data[["URI", "Name"]]
    combined_data = pd.concat([uri_name_table, new_data], ignore_index=True)
    # Check for duplicates between the new data and existing table
    combined_data.drop_duplicates(subset=["URI", "Name"], keep='first', inplace=True)
    
    # Identify new unique entries to insert
    unique_entries = combined_data[~combined_data.set_index(['URI', 'Name']).index.isin(uri_name_table.set_index(['URI', 'Name']).index)]

    # Append unique entries to the uri_name_table
    uri_name_table = pd.concat([uri_name_table, unique_entries], ignore_index=True)
    # Check for consistency after insertion
    check_uri_name_consistency()
    
def check_uri_name_consistency():
    """
    Checks for inconsistencies in the uri_name_table:
    - Duplicate URIs with different names
    - Duplicate Names with different URIs
    Displays warnings but does not modify the data.
    """
    global uri_name_table  # Use the global variable
    if uri_name_table is None:
        raise ValueError("Error: The uri_name_table is not initialized. Call init_uri_name() first.")

    # Find URIs with multiple names
    uri_duplicates = uri_name_table.groupby("URI")["Name"].nunique()
    uri_issues = uri_duplicates[uri_duplicates > 1]

    if not uri_issues.empty:
        for uri in uri_issues.index:
            associated_names = uri_name_table[uri_name_table['URI'] == uri]['Name'].unique()
            warnings.warn(f"⚠️ Inconsistency: URI '{uri}' is associated with multiple names: {', '.join(associated_names)}.")


    # Find Names with multiple URIs
    name_duplicates = uri_name_table.groupby("Name")["URI"].nunique()
    name_issues = name_duplicates[name_duplicates > 1]

    if not name_issues.empty:
        for name in name_issues.index:
            associated_uris = uri_name_table[uri_name_table['Name'] == name]['URI'].unique()
            warnings.warn(f"⚠️ Inconsistency: Name '{name}' is associated with multiple URIs: {', '.join(associated_uris)}.")

def getURIbyName(name):
    """
    Retrieves all URIs associated with the given name.
    
    Parameters:
    - name (str): The name for which to retrieve associated URIs.

    Returns:
    - str: A unique URI associated with the given name.

    Raises:
    - ValueError: If the name is empty, if no URIs are found, or if multiple URIs are found.
    """
    global uri_name_table  # Use the global variable
    if uri_name_table is None:
        raise ValueError("Error: The uri_name_table is not initialized.")

    if not name:
        raise ValueError("Error: The name cannot be empty.")

    uris = uri_name_table[uri_name_table["Name"] == name]["URI"].tolist()

    if len(uris) == 0:
        raise ValueError(f"Error: No URI found for '{name}'.")

    if len(uris) > 1:
        raise ValueError(f"Error: Multiple URIs found for '{name}': {uris}")

    return uris[0]  # Return the unique URI

def getNamesByURI(uri):
    """
    Retrieves all names associated with the given URI.
    Issues a warning if multiple names are found for the same URI.

    Parameters:
    - uri (str): The URI for which to retrieve associated names.

    Returns:
    - list: A list of names associated with the given URI. Returns an empty list if the URI is not found.
    """
    global uri_name_table  # Use the global variable
    if uri_name_table is None:
        raise ValueError("Error: The uri_name_table is not initialized. Call init_uri_name() first.")

    if not uri:  # Handle empty or None input
        warnings.warn("⚠️ Invalid input: URI cannot be empty or None.")
        return []

    names = uri_name_table[uri_name_table["URI"] == uri]["Name"].tolist()

    if not names:  # Handle case where the URI is not found
        warnings.warn(f"⚠️ No names found for the URI '{uri}'.")
        return []

    if len(names) > 1:
        warnings.warn(f"⚠️ Multiple names found for the URI '{uri}': {names}")

    return names


def print_table():
    """Prints the current state of the URI-Name table."""
    print("\nCurrent URI-Name table:")
    global uri_name_table  # Use the global variable
    # Vérifiez si la table existe et si elle n'est pas None
    if uri_name_table.empty:
        print("The table is empty.")
    else:
        print(uri_name_table.to_string(index=False))  # Display the table without the index
        
