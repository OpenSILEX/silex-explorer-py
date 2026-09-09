import requests
from tabulate import tabulate

from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

from ..exceptions import APIRequestError
from .ls_var_exp import get_ls_var_by_exp
from .get_exp_id import get_experiment_id
from .export_data import export_data_by_variable_to_csv


def fetch_chunk_data(chunk, experience, session):
    """Fetch data for a given chunk of OS URIs."""
    graphql_query = (
        """
        query ScientificObject($experience: [DataSource!]!, $osUris: [ID]) {
            ScientificObject(
                inferred: true,
                Experience: $experience,
                filter: {"""
        + ("_id: $osUris")
        + """}
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
    )

    variables = {"experience": experience, "osUris": chunk}

    response = requests.post(
        session["url_graphql"],
        json={"query": graphql_query, "variables": variables},
        headers=session["headers_graphql"],
    )

    list_data_os = []
    if response.status_code == 200:
        scientific_objects = response.json().get("data", {}).get("ScientificObject", [])
        for obj in scientific_objects:
            if "data" in obj and isinstance(obj["data"], list):
                list_data_os.extend(obj["data"])
    else:
        print(f"Error in chunk: {chunk}, status code: {response.status_code}, response: {response.text}")
        raise APIRequestError(f"Error: {response.status_code} - {response.text}")

    return list_data_os


def get_data_by_os_uri_variable(session, experiment_name, df_os, ls_var_exp=None, csv_filepath=None):
    """
    Retrieve data associated with scientific objects (OS) for a given experiment
    and organize the results by variable.

    The function fetches data in parallel for a list of scientific object URIs,
    groups the results by variable, and returns them as a dictionary of
    pandas DataFrames. Optionally, the extracted data can be exported to CSV
    files (one per variable) via the `export_data_by_variable_to_csv` function.

    Parameters
    ----------
    session : requests.Session
        Authenticated session used to communicate with the OpenSILEX API.

    experiment_name : str
        Name of the experiment used to retrieve the corresponding experiment URI.

    df_os : pandas.DataFrame
        DataFrame containing scientific objects.
        Must include a column named 'URI' with OpenSILEX object URIs.

    ls_var_exp : pandas.DataFrame, optional
        DataFrame listing the variables associated with the experiment.
        If None or empty, the variables are automatically retrieved
        using `get_ls_var_by_exp`.

    csv_filepath : str, optional
        Base file path or directory used to export variable-specific CSV files.
        If None, no CSV files are written.

    Returns
    -------
    dict[str, pandas.DataFrame]
        Dictionary where keys are variable identifiers and values are
        pandas DataFrames containing the associated data.
        Returns an empty dictionary if no data is found.
    """

    # Maximum number of OS URIs per API request
    max_ids_per_request = 40

    # Container for all retrieved results
    all_results = []

    # Retrieve experiment URI(s)
    experience = get_experiment_id(experiment_name, session)

    # Ensure experiment is always a list
    if isinstance(experience, str):
        experience = [experience]

    # Retrieve variables associated with the experiment if not provided
    if ls_var_exp is None or ls_var_exp.empty:
        ls_var_exp = get_ls_var_by_exp(session, experiment_name, page_size=20)

    # Validate input DataFrame
    if df_os is None or df_os.empty or "URI" not in df_os.columns:
        print("⚠️ Input DataFrame is empty or does not contain 'URI' column.")
        return {}

    # Extract scientific object URIs
    ls_os_uris = df_os["URI"].dropna().tolist()

    if not ls_os_uris:
        print("⚠️ No valid scientific object URIs found.")
        return {}

    # Split URIs into chunks
    chunks = list(chunk_list(ls_os_uris, max_ids_per_request))

    # Fetch data in parallel
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_chunk = {executor.submit(fetch_chunk_data, chunk, experience, session): chunk for chunk in chunks}

        all_results_lock = Lock()

        for i, future in enumerate(as_completed(future_to_chunk), start=1):
            try:
                data = future.result()
                print(f"Results for chunk {i}: {len(data)} items")

                with all_results_lock:
                    all_results.extend(data)
                    print(f"Total results collected: {len(all_results)} items")

            except Exception as exc:
                chunk = future_to_chunk[future]
                print(f"❌ Chunk {chunk} generated an exception: {exc}")

    # No data retrieved
    if not all_results:
        print("⚠️ No data found for the given experiment and scientific objects.")
        return {}

    # Organize data by variable and optionally export to CSV
    dataFrames = export_data_by_variable_to_csv(ls_var_exp, all_results, csv_filepath=csv_filepath)

    # Final safety check
    if not dataFrames:
        print("⚠️ Data retrieved but no variable-level DataFrames were generated.")

    return dataFrames


def chunk_list(data_list, chunk_size):
    """Divides a list into several sub-lists of size chunk_size."""
    for i in range(0, len(data_list), chunk_size):
        chunk = data_list[i : i + chunk_size]
        yield chunk
