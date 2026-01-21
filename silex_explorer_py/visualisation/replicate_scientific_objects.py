import pandas as pd
import seaborn as sns
import re
import matplotlib.pyplot as plt
from silex_explorer_py.experiment.chunk_data_exp import get_data_by_os_uri_variable
import os
import matplotlib.dates as mdates
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
    df[columns_to_compare] = df[columns_to_compare].applymap(str)

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


def visualize_replicate_groups(group_dict):
     # Set up the plotting style using seaborn
    sns.set(style="whitegrid")

    # Create a mapping of group identifiers to numerical values
    group_mapping = {group: idx for idx, group in enumerate(group_dict.keys())}
    
    # Visualize the distribution of groups based on their identifiers
    print("Visualizing the distribution of groups...")

    # Scatter plot to visualize group distribution
    plt.figure(figsize=(12, 6))
    all_groups = []
    all_indices = []
    
    # Prepare the scatter plot data
    for group, group_df in group_dict.items():
        all_groups.extend([group_mapping[group]] * len(group_df))  # Use numeric mapping
        all_indices.extend(group_df.index)  # Get the indices of the rows
        
    # Plot the scatter plot
    plt.scatter(all_indices, all_groups, c=all_groups, cmap="Set2", edgecolor='k', s=100)
    
    plt.title("Distribution of Scientific Objects across Groups")
    plt.xlabel("Index of Scientific Objects")
    plt.ylabel("Group Identifier")
    plt.colorbar(label="Group")
    plt.tight_layout()
    plt.show()
    
    

def print_group_summary(group_dict):
    # Print the number of groups and the names of the groups
    print(f"Total number of groups: {len(group_dict)}\n")
    
    # Print the names of each group along with the size of each group
    for group, group_df in group_dict.items():
        print(f"Group: {group}")
        print(f"Number of objects in this group: {len(group_df)}")
        print(f"First few entries in the group:\n{group_df.head()}\n")
        

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




def visualize_group_summary(group_dict):
    # Create a list to hold the group names and their corresponding sizes
    group_data = []

    # Iterate over the groups in the dictionary
    for group, group_df in group_dict.items():
        group_data.append([group, len(group_df)])  # Add the group name and size

    # Create a DataFrame from the list
    group_summary_df = pd.DataFrame(group_data, columns=['Group', 'Number of Elements'])

    # Plot the number of elements in each group
    plt.figure(figsize=(12, 6))  # Set the figure size
    plt.bar(group_summary_df['Group'], group_summary_df['Number of Elements'], color='skyblue')

    # Rotate the x-axis labels for better readability
    plt.xticks(rotation=90)

    # Add titles and labels
    plt.title('Distribution of Elements in Groups')
    plt.xlabel('Group')
    plt.ylabel('Number of Elements')

    # Show the plot
    plt.tight_layout()
    plt.show()
    
 

def visualize_scientific_data(df, variable_name):
    """
    Fonction pour visualiser les données d'une variable particulière pour plusieurs objets scientifiques.
    
    :param df: DataFrame contenant les données pour une variable particulière
    :param variable_name: Le nom de la variable à visualiser (ex: 'plant_height_ImageAnalysis_millimetre')
    :param date_column: Le nom de la colonne contenant les dates (par défaut 'Date')
    :param uri_column: Le nom de la colonne contenant les identifiants des objets scientifiques (par défaut 'URI')
    """
    
    # Convertir les dates en objets datetime (si ce n'est pas déjà le cas)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    # Trier les données par date
    df = df.sort_values(by='Date')
    # Créer une figure pour le graphique
    plt.figure(figsize=(10, 6))
    
    # Tracer une courbe pour chaque objet scientifique
    for uri in df['URI'].unique():
        # Filtrer les données pour cet objet scientifique
        data = df[df['URI'] == uri]
        
          # Vérifier s'il y a des valeurs manquantes pour cette série
        if data[variable_name].isna().any():  # Si des valeurs sont manquantes
            # Utiliser scatter plot si des valeurs manquantes
            plt.scatter(data['Date'], data[variable_name], label=uri)
        else:
            # Utiliser line plot si toutes les valeurs sont présentes
            plt.plot(data['Date'], data[variable_name], label=uri)
            
    # Ajouter des labels et un titre
    plt.xlabel('Date')
    plt.ylabel(variable_name.replace('_', ' ').capitalize())  # Capitaliser et enlever les underscores
    plt.title(f'Evolution de {variable_name.replace("_", " ").capitalize()}')
    plt.legend(title="Objets Scientifiques", bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Formatage des dates sur l'axe des x pour n'afficher que 'YYYY-MM-DD'
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    
    # Rotation des dates pour meilleure lisibilité
    plt.xticks(rotation=45)
    plt.tight_layout()  # Pour éviter que les labels se chevauchent
    
    # Afficher le graphique
    plt.show()
    

def visualize_all_variables(df_variables, csv_filepath=None):
    """
    Visualize all variables contained in a dictionary of DataFrames.

    Each variable is displayed in its own subplot within a single figure.
    Curves correspond to different scientific objects (URIs), and a shared
    legend is displayed for all subplots. The resulting figure can be exported
    as a PDF file.

    Parameters
    ----------
    df_variables : dict[str, pandas.DataFrame]
        Dictionary where:
        - keys are variable identifiers (e.g. 'df_height')
        - values are pandas DataFrames containing at least the columns:
          'URI', 'Date', and the variable name itself.

    csv_filepath : str, optional
        Path to the output PDF file.
        If None, the file is saved as 'visualization_output.pdf'
        in the current working directory.
        Parent directories are automatically created if they do not exist.

    Notes
    -----
    - Each subplot represents one variable.
    - Data are sorted by date before plotting.
    - Missing values are displayed as scatter points, while complete
      series are displayed as lines.
    - A common legend is shared across all subplots.
    """

    # Handle empty input
    if not df_variables:
        print("⚠️ No variables to visualize. The input dictionary is empty.")
        return

    # Determine the number of plots
    num_graphs = len(df_variables)
    if num_graphs == 0:
        print("⚠️ No data found in the variables dictionary.")
        return

    # Define subplot layout (2 plots per row)
    cols = 2
    rows = (num_graphs + cols - 1) // cols

    # Create the figure and subplots
    fig, axes = plt.subplots(rows, cols, figsize=(12, 6 * rows))
    axes = axes.flatten() if num_graphs > 1 else [axes]

    # Generate a color palette for multiple curves
    colors = sns.color_palette("tab10", n_colors=100)

    # Containers for shared legend handles and labels
    common_handles = []
    common_labels = []

    # Iterate over variables and create one subplot per variable
    for i, (key, df) in enumerate(df_variables.items()):
        # Skip empty DataFrames
        if df is None or df.empty:
            print(f"⚠️ DataFrame for variable '{key}' is empty. Skipping plot.")
            continue

        # Extract variable name by removing 'df_' prefix if present
        variable_name = key.replace('df_', '')

        # Check required columns
        if not all(col in df.columns for col in ['URI', 'Date', variable_name]):
            print(f"⚠️ DataFrame for variable '{key}' is missing required columns. Skipping plot.")
            continue

        # Convert 'Date' column to datetime
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

        # Sort values by date
        df = df.sort_values(by='Date')

        # Select the corresponding subplot axis
        ax = axes[i]

        # Plot one curve per scientific object (URI)
        for j, uri in enumerate(df['URI'].unique()):
            data = df[df['URI'] == uri]

            if data[variable_name].isna().any():
                ax.scatter(
                    data['Date'],
                    data[variable_name],
                    label=uri,
                    color=colors[j % len(colors)]
                )
            else:
                ax.plot(
                    data['Date'],
                    data[variable_name],
                    label=uri,
                    color=colors[j % len(colors)]
                )

        # Set subplot title and axis labels
        ax.set_title(variable_name.replace("_", " ").capitalize())
        ax.set_xlabel("Date")
        ax.set_ylabel(variable_name.replace("_", " ").capitalize())

        # Store legend handles from the first subplot only
        if not common_handles and not common_labels:
            common_handles, common_labels = ax.get_legend_handles_labels()

        # Format x-axis as dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.tick_params(axis='x', rotation=45)

    # Adjust layout to avoid overlap
    plt.tight_layout()

    # Add a shared legend below all subplots if handles exist
    if common_handles and common_labels:
        fig.legend(
            common_handles,
            common_labels,
            loc='upper center',
            bbox_to_anchor=(0.5, -0.1),
            ncol=2
        )

    # Define output file path
    if csv_filepath is None:
        csv_filepath = "visualization_output.pdf"

    # Ensure output directory exists
    if os.path.dirname(csv_filepath):
        os.makedirs(os.path.dirname(csv_filepath), exist_ok=True)

    # Save the figure as a PDF
    pdf_file = os.path.join(csv_filepath, "visualisation_output.pdf")
    plt.savefig(pdf_file, bbox_inches='tight')
    print(f"✅ Visualization PDF has been saved to '{pdf_file}'.")

    # Display the figure
    plt.show()

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

def compare_groups_by_factor_level(group_dict, session, experiment_name,
                                   group1_id, group2_id, factor,
                                   csv_filepath=None):
    """
    Compare two groups by a factor level, transform data, save outputs, and plot time series.

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
        Column name containing the factor level (e.g., 'level').
    csv_filepath : str, optional
        Path to save outputs (CSV + PDFs). Can be a folder or a file path.
        If None, the folder "output" is created in the current working directory.

    Returns
    -------
    pandas.DataFrame
        Combined DataFrame with columns ['Date','URI','Groupe',factor,'Variable','Valeur'].
    """

    # 1️⃣ Transform data
    df_final = transform_data_for_plot(
        group_dict, session, experiment_name,
        group1_id, group2_id, factor
    )

    if df_final.empty:
        print("⚠️ No data to process. Exiting.")
        return df_final

    # 2️⃣ Determine output directory
    if csv_filepath is None:
        output_dir = "output"
    elif os.path.isdir(csv_filepath) or not os.path.splitext(csv_filepath)[1]:
        output_dir = csv_filepath
    else:
        output_dir = os.path.dirname(csv_filepath) or "output"

    os.makedirs(output_dir, exist_ok=True)

    # Save combined CSV
    csv_file = os.path.join(output_dir, "data.csv")
    df_final.to_csv(csv_file, index=False)
    print(f"✅ Combined CSV saved at '{csv_file}'.")

    # 3️⃣ Prepare plotting
    df_final['Date'] = pd.to_datetime(df_final['Date'], errors='coerce')
    df_final = df_final.sort_values(by='Date')

    groupes_uniques = df_final['Groupe'].unique()
    palette = sns.color_palette("husl", len(groupes_uniques))
    palette_dict = dict(zip(groupes_uniques, palette))

    variables = df_final['Variable'].unique()

    for var in variables:
        plt.figure(figsize=(12, 5))

        # 🔹 Graph 1: All OS curves colored by group
        plt.subplot(1, 2, 1)
        sns.lineplot(
            data=df_final[df_final['Variable'] == var],
            x="Date", y="Valeur", hue="Groupe",
            style="Groupe", units="URI", estimator=None,
            lw=1, alpha=0.5, palette=palette_dict, dashes=False
        )
        match = re.match(r"[^_]+_([^_]+)", var)
        extracted_part = match.group(1) if match else var
        plt.title(f"Évolution des OS - {extracted_part}")
        plt.xlabel("Date")
        plt.ylabel(var)
        plt.xticks(rotation=45, ha="right")

        # 🔹 Graph 2: Mean per group with SD
        plt.subplot(1, 2, 2)
        sns.lineplot(
            data=df_final[df_final['Variable'] == var],
            x="Date", y="Valeur", hue="Groupe",
            style="Groupe", markers=True, lw=3, dashes=False,
            errorbar="sd", palette=palette_dict
        )
        plt.title(f"Moyenne des groupes - {extracted_part}")
        plt.xlabel("Date")
        plt.ylabel(var)
        plt.xticks(rotation=45, ha="right")

        plt.tight_layout()

        # Save PDF
        pdf_file = os.path.join(output_dir, f"{var}.pdf")
        plt.savefig(pdf_file, bbox_inches='tight')
        print(f"✅ PDF saved for variable '{var}' at '{pdf_file}'.")
        plt.show()

    return df_final


def plot_time_series(df):
    """
    Affiche des courbes temporelles pour chaque variable mesurée.

    Parameters:
        - df : DataFrame contenant les données avec les colonnes ['Date', 'Groupe', 'Variable', 'Valeur'].
    
    Returns:
        - Affiche un graphique par variable.
    """
    # Liste des variables uniques
    variables = df['Variable'].unique()
    
    # Convertir la colonne 'Date' en datetime si ce n'est pas déjà fait
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
    # Trier les données par date
    df = df.sort_values(by='Date')
    # Création de la figure
    plt.figure(figsize=(12, 8))

    for i, var in enumerate(variables, 1):
        plt.subplot(2, 2, i)  # 2 lignes, 2 colonnes (modulable selon le nombre de variables)
        sns.lineplot(data=df[df['Variable'] == var], 
                     x="Date", y="Valeur", hue="Groupe", 
                     style="Groupe", markers=True, dashes=False, ci="sd")

        plt.title(var)
        plt.xlabel("Date")
        plt.ylabel(var)

    plt.tight_layout()
    plt.show()
    
def plot_time_series_with_individuals(df):
    """
    Affiche les courbes temporelles pour chaque variable avec :
    - Une courbe par OS (fine et transparente)
    - Une courbe moyenne par groupe (épaisse)
    
    Parameters:
        - df : DataFrame contenant les colonnes ['Date', 'URI', 'Groupe', 'Variable', 'Valeur'].
    
    Returns:
        - Affiche un graphique par variable.
    """
    variables = df['Variable'].unique()
    
     # Convertir la colonne 'Date' en datetime si ce n'est pas déjà fait
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
    # Trier les données par date
    df = df.sort_values(by='Date')
    
    plt.figure(figsize=(12, 8))

    for i, var in enumerate(variables, 1):
        plt.subplot(2, 2, i)
        
        # Tracer les courbes individuelles par OS
        sns.lineplot(data=df[df['Variable'] == var], 
                     x="Date", y="Valeur", hue="URI", 
                     style="Groupe", lw=1, alpha=0.3, legend=False)  # Courbes fines
        
        # Tracer la moyenne par groupe
        sns.lineplot(data=df[df['Variable'] == var], 
                     x="Date", y="Valeur", hue="Groupe", 
                     style="Groupe", markers=True, lw=3, dashes=False, ci="sd")  # Courbes moyennes

        plt.title(var)
        plt.xlabel("Date")
        plt.ylabel(var)

    plt.tight_layout()
    plt.show()


