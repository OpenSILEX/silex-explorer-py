import os
import re

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages

from ..experiment.chunk_data_exp import get_data_by_os_uri_variable

def replicate_scientific_objects(df, csv_filepath=None):
    """
    Group scientific objects based on variable combinations and optionally
    generate a CSV summary of the resulting groups.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame containing scientific objects metadata.
        Must include at least the columns 'URI' and 'Name'.

    csv_filepath : str, optional
        Path to the CSV file where the group summary will be saved.
        If None, no CSV file is generated.
        Parent directories are automatically created if they do not exist.

    Returns
    -------
    dict
        Dictionary where keys are group identifiers and values are DataFrames
        corresponding to each group.
    """

    # Exclude 'URI' and 'Name' columns from the comparison
    columns_to_compare = [
        col for col in df.columns if col not in ['URI', 'Name']
    ]
    
    # Exclude columns where all values are identical
    columns_to_compare = [
        col for col in columns_to_compare
        if df[col].nunique(dropna=False) > 1
    ]

    # Convert all values in relevant columns to string to avoid type issues
    df[columns_to_compare] = df[columns_to_compare].astype(str)
    # Function to remove trailing NaNs from the group identifier
    def remove_trailing_nans_from_identifier(group_identifier):
        """
        Remove trailing 'nan' values only at the end of the group identifier.
        """
        parts = group_identifier.split('_')
        while parts and parts[-1] == 'nan':
            parts.pop()
        return '_'.join(parts)

    # Create a unique identifier for each row based on selected columns
    df['group_identifier'] = df[columns_to_compare].agg('_'.join, axis=1)

    # Clean group identifiers by removing trailing NaNs
    df['group_identifier'] = df['group_identifier'].apply(
        remove_trailing_nans_from_identifier
    )

    # Assign a default identifier if the result is empty
    df['group_identifier'] = df['group_identifier'].apply(
        lambda x: x if x != '' else 'NaN_group'
    )

    # Dictionary to store grouped DataFrames
    group_dict = {}

    # List to store group summary information
    group_summary = []

    # Group DataFrame by group identifier
    for group, group_df in df.groupby('group_identifier'):
        # Store group DataFrame without the group identifier column
        group_dict[group] = group_df.drop(columns=['group_identifier'])
        # Store group name and number of elements
        group_summary.append([group, len(group_df)])

    # Save group summary to CSV if requested
    if csv_filepath:
        # Ensure output directory exists
        if os.path.dirname(csv_filepath):
            os.makedirs(os.path.dirname(csv_filepath), exist_ok=True)

        # Create and save the summary DataFrame
        group_summary_df = pd.DataFrame(
            group_summary,
            columns=['Group', 'Number of Elements']
        )
        group_summary_df.to_csv(csv_filepath, index=False)
        print(f"✅ Group summary has been saved to '{csv_filepath}'.")

    return group_dict

   
        
def extract_group_os(group_dict, group_identifier, csv_filepath=None):
    """
    Extract a specific group of scientific objects from a grouped dictionary
    and optionally save it to a CSV file.

    Parameters
    ----------
    group_dict : dict
        Dictionary of grouped DataFrames, typically returned by
        `replicate_scientific_objects`.
        Keys are group identifiers and values are pandas DataFrames.

    group_identifier : str
        Identifier of the group to extract.
        Must exactly match one of the keys in `group_dict`.

    csv_filepath : str, optional
        Path to the CSV file where the extracted group will be saved.
        If None, the group is not written to disk.
        Parent directories are automatically created if they do not exist.

    Returns
    -------
    pandas.DataFrame or None
        The DataFrame corresponding to the selected group if it exists.
        Returns None if the group identifier is not found.

    Notes
    -----
    - The CSV file is written without the index column.
    - If the provided group identifier does not exist, a warning message
      is printed and no file is created.

    Example
    -------
    >>> group_df = extract_group_os(
    ...     group_dict,
    ...     group_identifier="WD_ScionLot_ZM4383_Zea mays",
    ...     csv_filepath="outputs/group_WD_ScionLot_ZM4383_Zea mays.csv"
    ... )
    """

    # Check if the requested group exists
    if group_identifier not in group_dict:
        print(
            f"❌ Invalid group identifier. "
            f"Available groups: {list(group_dict.keys())}"
        )
        return None

    # Retrieve the DataFrame for the requested group
    group_df = group_dict[group_identifier]

    # Save to CSV if requested
    if csv_filepath:
        # Ensure output directory exists
        if os.path.dirname(csv_filepath):
            os.makedirs(os.path.dirname(csv_filepath), exist_ok=True)

        group_df.to_csv(csv_filepath, index=False)
        print(f"✅ Group '{group_identifier}' has been saved to '{csv_filepath}'.")

    return group_df


def visualize_all_variables(df_variables, pdf_filepath=None):
    """
    Visualize all variables contained in a dictionary of DataFrames.
    Several graphs are displayed per PDF page to keep them readable.

    Parameters
    ----------
    df_variables : dict[str, pandas.DataFrame]
        Dictionary where keys are variable identifiers and values are DataFrames.

    pdf_filepath : str, optional
        Output PDF file.
    """

    if not df_variables:
        print("⚠️ No variables to visualize.")
        return

    valid_variables = {
        key: df
        for key, df in df_variables.items()
        if df is not None and not df.empty
    }

    if not valid_variables:
        print("⚠️ No non-empty variables to visualize.")
        return

    if pdf_filepath is None:
        pdf_filepath = "visualization_output.pdf"

    output_dir = os.path.dirname(pdf_filepath)

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # --------------------------------------------------
    # Configuration
    # --------------------------------------------------

    cols = 2
    rows = 3

    graphs_per_page = cols * rows  # 6 graphiques par page

    colors = sns.color_palette("tab10", n_colors=100)

    variables = list(valid_variables.items())

    # --------------------------------------------------
    # PDF multipage
    # --------------------------------------------------

    with PdfPages(pdf_filepath) as pdf:

        for page_start in range(0, len(variables), graphs_per_page):

            page_variables = variables[
                page_start:page_start + graphs_per_page
            ]

            fig, axes = plt.subplots(
                rows,
                cols,
                figsize=(16, 12)
            )

            axes = axes.flatten()

            common_handles = []
            common_labels = []

            # ------------------------------------------
            # Graphs de la page
            # ------------------------------------------

            for i, (key, df) in enumerate(page_variables):

                variable_name = key.replace("df_", "")

                ax = axes[i]

                required = [
                    "URI",
                    "Date",
                    variable_name
                ]

                if not all(col in df.columns for col in required):

                    ax.text(
                        0.5,
                        0.5,
                        f"Missing columns\n{variable_name}",
                        horizontalalignment="center",
                        verticalalignment="center",
                        transform=ax.transAxes
                    )

                    ax.set_axis_off()

                    print(
                        f"⚠️ Missing columns for '{variable_name}'."
                    )

                    continue

                data_df = df.copy()

                data_df["Date"] = pd.to_datetime(
                    data_df["Date"],
                    errors="coerce"
                )

                data_df = data_df.dropna(
                    subset=["Date"]
                )

                data_df = data_df.sort_values(
                    "Date"
                )

                # --------------------------------------
                # Une courbe par URI
                # --------------------------------------

                for j, uri in enumerate(
                    data_df["URI"].dropna().unique()
                ):

                    data = data_df[
                        data_df["URI"] == uri
                    ]

                    color = colors[
                        j % len(colors)
                    ]

                    if data[variable_name].notna().sum() <= 1:

                        ax.scatter(
                            data["Date"],
                            data[variable_name],
                            color=color,
                            label=uri,
                            s=30
                        )

                    else:

                        ax.plot(
                            data["Date"],
                            data[variable_name],
                            color=color,
                            label=uri,
                            linewidth=1.8,
                            marker="o",
                            markersize=3
                        )

                # --------------------------------------
                # Titre
                # --------------------------------------

                title = variable_name.replace(
                    "_",
                    " "
                )

                ax.set_title(
                    title,
                    fontsize=10,
                    fontweight="bold",
                    pad=8
                )

                # --------------------------------------
                # Grille
                # --------------------------------------

                ax.grid(
                    True,
                    linestyle="--",
                    alpha=0.3
                )

                # --------------------------------------
                # Dates
                # --------------------------------------

                locator = mdates.AutoDateLocator(
                    minticks=3,
                    maxticks=6
                )

                formatter = mdates.ConciseDateFormatter(
                    locator
                )

                ax.xaxis.set_major_locator(
                    locator
                )

                ax.xaxis.set_major_formatter(
                    formatter
                )

                ax.tick_params(
                    axis="x",
                    labelsize=8
                )

                ax.tick_params(
                    axis="y",
                    labelsize=8
                )

                # --------------------------------------
                # Legend commune
                # --------------------------------------

                if not common_handles:

                    common_handles, common_labels = (
                        ax.get_legend_handles_labels()
                    )

            # ------------------------------------------
            # Cacher cases inutilisées
            # ------------------------------------------

            for i in range(
                len(page_variables),
                len(axes)
            ):
                axes[i].set_visible(False)

            # ------------------------------------------
            # Legend commune
            # ------------------------------------------

            if common_handles:

                fig.legend(
                    common_handles,
                    common_labels,
                    loc="lower center",
                    bbox_to_anchor=(0.5, 0.01),
                    ncol=min(
                        5,
                        len(common_labels)
                    ),
                    fontsize=8
                )

            # ------------------------------------------
            # Espacement
            # ------------------------------------------

            fig.subplots_adjust(
                left=0.07,
                right=0.98,
                top=0.95,
                bottom=0.10,
                hspace=0.45,
                wspace=0.25
            )

            # ------------------------------------------
            # Sauvegarde de la page
            # ------------------------------------------

            pdf.savefig(
                fig,
                bbox_inches="tight"
            )

            plt.show()

            plt.close(fig)

    print(
        f"✅ Visualization saved to '{pdf_filepath}'."
    )

def transform_data_for_plot(group_dict, session, experiment_name, 
                            group1_id, group2_id, factor):
    """
    Prépare les données pour une visualisation en courbes temporelles,
    en utilisant les identifiants de groupe au lieu des numéros.

    Parameters:
        - group_dict : dictionnaire contenant tous les groupes (clé = identifiant).
        - session : session pour OpenSILEX API.
        - experiment_name : nom de l'expérience.
        - group1_id, group2_id : identifiants des deux groupes à comparer.
        - factor : nom de la colonne contenant le niveau du facteur .

    Returns:
        - Un DataFrame avec les colonnes : Date, URI, Groupe, Variable, Valeur
    """

    # 1️⃣ Récupérer les DataFrames des deux groupes par identifiant
    df_os1 = extract_group_os(group_dict, group_identifier=group1_id)
    df_os2 = extract_group_os(group_dict, group_identifier=group2_id)

    # Vérifier si les DataFrames sont vides
    if df_os1.empty and df_os2.empty:
        print("⚠️ Les deux groupes sont vides. Aucune donnée à traiter.")
        return pd.DataFrame()

    # 2️⃣ Récupérer les données des variables pour chaque groupe
    df_var1 = get_data_by_os_uri_variable(session, experiment_name, df_os1)
    df_var2 = get_data_by_os_uri_variable(session, experiment_name, df_os2)

    # 3️⃣ Ajouter les colonnes "Groupe" et "Factor Level"
    for var in df_var1.keys():
        df_var1[var]['Groupe'] = f"{factor.capitalize()} {df_os1[factor].iloc[0]}" if not df_os1.empty else None
        df_var1[var][factor] = df_os1[factor].iloc[0] if not df_os1.empty else None

        df_var2[var]['Groupe'] = f"{factor.capitalize()} {df_os2[factor].iloc[0]}" if not df_os2.empty else None
        df_var2[var][factor] = df_os2[factor].iloc[0] if not df_os2.empty else None

    # 4️⃣ Rassembler toutes les variables en un seul DataFrame
    df_list = []
    for var in df_var1.keys():
        cleaned_var = var.replace('df_', '')

        if not df_var1[var].empty:
            df_temp1 = df_var1[var].copy()
            df_temp1['Variable'] = cleaned_var
            df_temp1 = df_temp1[['Date', 'URI', 'Groupe', factor, 'Variable', cleaned_var]]
            df_temp1 = df_temp1.rename(columns={cleaned_var: 'Valeur'})
            df_list.append(df_temp1)

        if not df_var2[var].empty:
            df_temp2 = df_var2[var].copy()
            df_temp2['Variable'] = cleaned_var
            df_temp2 = df_temp2[['Date', 'URI', 'Groupe', factor, 'Variable', cleaned_var]]
            df_temp2 = df_temp2.rename(columns={cleaned_var: 'Valeur'})
            df_list.append(df_temp2)

    if not df_list:
        print("⚠️ Aucun résultat obtenu pour les variables. DataFrame final vide.")
        return pd.DataFrame()

    # 5️⃣ Concaténer
    df_final = pd.concat(df_list, ignore_index=True)
    return df_final

def compare_groups_by_factor_level(
    group_dict,
    session,
    experiment_name,
    group1_id,
    group2_id,
    factor,
    csv_filepath=None,
    pdf_filepath=None
):
    """
    Compare two groups by a factor level, transform data,
    save outputs, and plot time series.

    All visualizations are saved in a single multipage PDF.

    Parameters
    ----------
    group_dict : dict
        Dictionary containing all groups (keys = identifiers or IDs).

    session : requests.Session
        Authenticated session for OpenSILEX API.

    experiment_name : str
        Name of the experiment to fetch data from.

    group1_id, group2_id : str
        Identifiers of the two groups to compare.

    factor : str
        Column name containing the factor level
        (e.g. "Water Level").

    csv_filepath : str, optional
        Path of the output CSV file.

    pdf_filepath : str, optional
        Path of the output multipage PDF file.

    Returns
    -------
    pandas.DataFrame
        Combined DataFrame with columns:
        ['Date', 'URI', 'Groupe', factor, 'Variable', 'Valeur']
    """

    # --------------------------------------------------
    # 1. Transform data
    # --------------------------------------------------

    df_final = transform_data_for_plot(
        group_dict,
        session,
        experiment_name,
        group1_id,
        group2_id,
        factor
    )

    # Protection against None
    if df_final is None:
        print("⚠️ transform_data_for_plot returned None.")
        return None

    if df_final.empty:
        print("⚠️ No data to process. Exiting.")
        return df_final

    # --------------------------------------------------
    # 2. Default output paths
    # --------------------------------------------------

    if csv_filepath is None:
        csv_filepath = os.path.join(
            "output",
            "data.csv"
        )

    if pdf_filepath is None:
        pdf_filepath = os.path.join(
            "output",
            "comparison_groups.pdf"
        )

    # --------------------------------------------------
    # 3. Create output directories
    # --------------------------------------------------

    csv_dir = os.path.dirname(csv_filepath)

    if csv_dir:
        os.makedirs(
            csv_dir,
            exist_ok=True
        )

    pdf_dir = os.path.dirname(pdf_filepath)

    if pdf_dir:
        os.makedirs(
            pdf_dir,
            exist_ok=True
        )

    # --------------------------------------------------
    # 4. Save combined CSV
    # --------------------------------------------------

    df_final.to_csv(
        csv_filepath,
        index=False
    )

    print(
        f"✅ Combined CSV saved at "
        f"'{csv_filepath}'."
    )

    # --------------------------------------------------
    # 5. Prepare plotting
    # --------------------------------------------------

    df_final["Date"] = pd.to_datetime(
        df_final["Date"],
        errors="coerce"
    )

    df_final = df_final.sort_values(
        by="Date"
    )

    # --------------------------------------------------
    # Groups and colors
    # --------------------------------------------------

    groupes_uniques = (
        df_final["Groupe"]
        .dropna()
        .unique()
    )

    palette = sns.color_palette(
        "husl",
        len(groupes_uniques)
    )

    palette_dict = dict(
        zip(
            groupes_uniques,
            palette
        )
    )

    # --------------------------------------------------
    # Variables
    # --------------------------------------------------

    variables = (
        df_final["Variable"]
        .dropna()
        .unique()
    )

    # --------------------------------------------------
    # 6. Create ONE multipage PDF
    # --------------------------------------------------

    with PdfPages(pdf_filepath) as pdf:

        for var in variables:

            var_df = df_final[
                df_final["Variable"] == var
            ]

            if var_df.empty:
                continue

            # ==========================================
            # Create figure
            # ==========================================

            fig, axes = plt.subplots(
                1,
                2,
                figsize=(12, 5)
            )

            # ==========================================
            # Graph 1
            # All OS curves colored by group
            # ==========================================

            sns.lineplot(
                data=var_df,
                x="Date",
                y="Valeur",
                hue="Groupe",
                style="Groupe",
                units="URI",
                estimator=None,
                lw=1,
                alpha=0.5,
                palette=palette_dict,
                dashes=False,
                ax=axes[0]
            )

            # Extract readable variable name
            match = re.match(
                r"[^_]+_([^_]+)",
                str(var)
            )

            extracted_part = (
                match.group(1)
                if match
                else str(var)
            )

            axes[0].set_title(
                f"Évolution des OS - "
                f"{extracted_part}"
            )

            axes[0].set_xlabel("Date")
            axes[0].set_ylabel(str(var))

            axes[0].tick_params(
                axis="x",
                rotation=45
            )

            # ==========================================
            # Graph 2
            # Mean per group + SD
            # ==========================================

            sns.lineplot(
                data=var_df,
                x="Date",
                y="Valeur",
                hue="Groupe",
                style="Groupe",
                markers=True,
                lw=3,
                dashes=False,
                errorbar="sd",
                palette=palette_dict,
                ax=axes[1]
            )

            axes[1].set_title(
                f"Moyenne des groupes - "
                f"{extracted_part}"
            )

            axes[1].set_xlabel("Date")
            axes[1].set_ylabel(str(var))

            axes[1].tick_params(
                axis="x",
                rotation=45
            )

            # ==========================================
            # Layout
            # ==========================================

            fig.tight_layout()

            # ==========================================
            # Add this figure as ONE page
            # ==========================================

            pdf.savefig(
                fig,
                bbox_inches="tight"
            )

            print(
                f"✅ Variable '{var}' added to PDF."
            )

            # Display
            plt.show()

            # Free memory
            plt.close(fig)

    # --------------------------------------------------
    # 7. Final message
    # --------------------------------------------------

    print(
        f"✅ Multipage PDF saved at "
        f"'{pdf_filepath}'."
    )

    return df_final