import os
from collections import defaultdict

import pandas as pd


def export_data_by_variable_to_csv(var_exp, data, csv_filepath=None):
    """
    Export data to CSV files organized by variable.

    Args:
        var_exp (pd.DataFrame): DataFrame containing variables.
        data (list): List of dictionaries containing data.
        csv_filepath (str, optional): Directory where CSV files are saved.

    Returns:
        dict: Dictionary where keys are variable names and values are DataFrames.
    """

    if var_exp is None or var_exp.empty:
        print("Warning: No variables provided. Nothing to export.")
        return

    if not data:
        print("Warning: No data provided. Nothing to export.")
        return

    variable_data = defaultdict(list)

    uri_to_name = var_exp.set_index("URI")["Name"].to_dict()

    if "URI" in var_exp.columns:
        variables = var_exp["URI"].dropna().tolist()

    for item in data:
        if not variables or item["variable"] in variables:
            variable_data[item["variable"]].append(
                (item["target"], item["value"], item["date"])
            )

    if not variable_data:
        print("Warning: No data matched the variables provided.")
        return

    dataframes = {}

    for variable, measurements in variable_data.items():
        variable_name = uri_to_name.get(
            variable,
            variable.split("/")[-1]
        )

        df = pd.DataFrame(
            measurements,
            columns=["URI", variable_name, "Date"]
        )

        dataframes[f"df_{variable_name}"] = df

        if csv_filepath:
            os.makedirs(csv_filepath, exist_ok=True)

            csv_filename = os.path.join(
                csv_filepath,
                f"{variable_name}_data.csv"
            )

            df.to_csv(csv_filename, index=False)

            print(
                f"✅ Data for variable '{variable_name}' "
                f"has been saved to '{csv_filename}'."
            )

    return dataframes