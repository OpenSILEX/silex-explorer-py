# Documentation of `get_os_by_exp` function

## Description

The `get_os_by_exp` function retrieves scientific objects associated with a given experiment and object type, with optional dynamic filtering based on factor levels and germplasm. The function sends a GraphQL query to fetch the scientific objects, processes the response, and saves the data into a CSV file. The filtering options allow you to refine the results based on specific conditions such as factor levels, germplasm type, and germplasm name.

## Arguments

- **session (dict)**:  
  - The authentication session containing the necessary GraphQL endpoint and headers.

- **experience (str)**:  
  - Name and beggining date of the experiment, used to filter the scientific objects ex :'ZA17_2017_03_30'.

- **obj_type (str)**:  
  - URI of the object type to filter.

- **factor_level_uri (str, optional)**:  
  - Factor level URI to filter the scientific objects. Default is `None`.

- **germplasm_uri (str, optional)**:  
  - Germplasm URI to filter the scientific objects. Default is `None`.

- **factor_levels (list, optional)**:  
  - List of factor levels in the format 'factor.factorlevel' to filter the scientific objects. Default is `None`.

- **germplasm_type (str, optional)**:  
  - Type of germplasm to filter by. Default is `None`.

- **germplasm_name (str, optional)**:  
  - Name of the germplasm to filter by. Default is `None`.If provided, you **must** also specify `germplasm_type`.

- **csv_filename (str, optional)**:  
  - The filename for the output CSV file. Default is `'scientific_objects.csv'`.

## Returns

- **pd.DataFrame**:  
  - A DataFrame containing detailed information about the scientific objects:
    - `uri`: URI of the scientific object.
    - `name`: Name of the scientific object.
    - `type`: Type of the scientific object.
    - `factor_name`: Factor name(s) associated with the object.
        - The name(s) of the factor(s) associated with the scientific object. For each factor associated with the objects, a separate column will be created in the DataFrame.
        - The value(s) in the column will correspond to the **factor level(s)** applied to the object for that factor. For example, if an object is associated with a **"temperature"** factor, the column name will be "temperature", and its value will be the factor level(s) (e.g., "high", "low") for that object.
    - `germplasm_type`: Germplasm type(s) associated with the object (e.g., Variety, Species, Accession, SeedLot etc).
    - `germplasm_name`:Name(s) of the germplasm associated with the scientific object. 
    - `Species`: Species associated with the germplasm.
    - `Variety`: Variety associated with the germplasm.
    - `Accession`: Accession associated with the germplasm.


The structure of the **germplasm-related columns** depends on the **germplasm type** and the number of germplasms associated with the object. To differentiate between multiple germplasms linked to the same scientific object, the columns will be indexed with `_1`, `_2`, etc., for each germplasm.

- If the **germplasm type** is `SeedLot`, all the following columns will be populated:
    - **`germplasm_type_1`**: Type of the first germplasm (e.g., `seedLot`).
    - **`germplasm_name_1`**: Name of the first germplasm.
    - **`Variety_1`**: Variety associated with the first germplasm.
    - **`Species_1`**: Species associated with the first germplasm.
    - **`Accession_1`**: Accession associated with the first germplasm.
    - For any additional germplasm associated with the same scientific object, the columns will be indexed as `_2`, `_3`, etc. (e.g., `germplasm_type_2`, `germplasm_name_2`, `Species_2`, `Variety_2`, etc.).

- If the **germplasm type** is `Accession`, the following columns will be populated:
    - **`germplasm_type_1`**: Type of the first germplasm (e.g., `accession`).
    - **`germplasm_name_1`**: Name of the first germplasm.
    - **`Variety_1`**: Variety associated with the first germplasm.
    - **`Species_1`**: Species associated with the first germplasm.

- If the **germplasm type** is `Variety`, the following columns will be populated:
    - **`germplasm_type_1`**: Type of the first germplasm (e.g., `Variety`).
    - **`germplasm_name_1`**: Name of the first germplasm.
    - **`Species_1`**: Species associated with the first germplasm.
  
- If the **germplasm type** is `Species`, only the following columns will be populated:
    - **`germplasm_type_1`**: Type of the first germplasm (e.g., `species`).
    - **`germplasm_name_1`**: Name of the first germplasm.

### Example:
Suppose a scientific object has **two germplasms** associated with it:

- **First germplasm** of type `Accession` (which includes `germplasm_type`, `germplasm_name`, `Variety` and  `Species`).
- **Second germplasm** of type `Species` (which only includes `germplasm_type`and `germplasm_name`).

The resulting DataFrame will look like this:

| uri   | name  | type  | temperature | germplasm_type_1 | germplasm_name_1 | variety_1 | species_1 | germplasm_type_2 | germplasm_name_2 |
|-------|-------|-------|-------------|------------------|------------------|-----------|-----------|------------------|------------------|
| URI1  | Obj1  | Type  | high        | accession        | Germplasm1       | Variety1  | Species1  | species          | Germplasm2       |


This structure allows you to easily distinguish between multiple germplasms associated with a single scientific object, with each germplasm having its own set of columns for type, name, variety, species, and accession.

## Example Usage
## 1. Filtering by Germplasm Type Only

In this example, the filter is applied based on the **germplasm type** only. The user specifies the `germplasm_type` without any additional filtering on the specific germplasm URI or factor levels.

```python
from package.exceptions.custom_exceptions import APIRequestError
from package.experiment.ls_scientific_objects import get_os_by_exp

# Assuming `session` is already defined with authentication details
experiment = "ZA17_2017_03_30"  # Replace with the actual experiment ID
obj_type = "http://www.opensilex.org/vocabulary/oeso#Plant"  # Replace with the actual object type URI
germplasm_type = "Species"  # Filter for all scientific objects related to species-type germplasm

df = get_os_by_exp(
    session, 
    experiment, 
    obj_type, 
    germplasm_type=germplasm_type
)
print(df.head())
```
#### Explanation:

- **germplasm_type**: Filters scientific objects based on the type of germplasm, e.g., Species, Variety, Accession,SeedLot etc.  
This example will return all scientific objects associated with a `Species` type germplasm.

## 2. Filtering by Germplasm Type and Germplasm Name

This third example filters using both **germplasm type** and **germplasm name**. The filter is applied based on the type and name of the germplasm, regardless of whether the germplasm is part of a lower-level hierarchy (such as Accession or Species).

```python
from package.exceptions.custom_exceptions import APIRequestError
from package.experiment.ls_scientific_objects import get_os_by_exp

# Assuming `session` is already defined with authentication details
experiment = "ZA17_2017_03_30"  # Replace with the actual experiment ID
obj_type = "http://www.opensilex.org/vocabulary/oeso#Plant"  # Replace with the actual object type URI
germplasm_type = "Species"  # Specify germplasm type (e.g., species)
germplasm_name = "GermplasmName"  # Specify germplasm name (e.g., name of the Species)

df = get_os_by_exp(
    session, 
    experiment, 
    obj_type, 
    germplasm_type=germplasm_type, 
    germplasm_name=germplasm_name
)
print(df.head())
```
#### Explanation:

- **germplasm_type**: Filters scientific objects based on the type of germplasm (e.g., Species, Variety, Accession).
- **germplasm_name**: Filters scientific objects based on the name of the germplasm (e.g., a specific Species name).

In this case, the filter applies to **`all scientific objects`** associated with the specified **Species**, regardless of the hierarchical level of the germplasm (i.e., whether it's at the Species, Variety, or Accession level). This means that even if the germplasm is of a lower type, such as an Accession, the filter will return all scientific objects linked to that Species.


## 3. Filtering by Germplasm URI and Factor URI

In this example, the filter applies both **germplasm URI** and **factor level URI**. The germplasm URI filter only applies to the lowest level of the germplasm hierarchy.

```python
from package.exceptions.custom_exceptions import APIRequestError
from package.experiment.ls_scientific_objects import get_os_by_exp

# Assuming `session` is already defined with authentication details
experiment = "ZA17_2017_03_30"  # Replace with the actual experiment ID
obj_type = "http://www.opensilex.org/vocabulary/oeso#Plant"  # Replace with the actual object type URI
factor_level_uri = ["http://example.org/factor/Factor1.Level1"]  # Example URI of the factor level to filter
germplasm_uri = ["http://example.org/germplasm/species1"]  # Example URI of the germplasm (can be species, variety, etc.)

df = get_os_by_exp(
    session, 
    experiment, 
    obj_type, 
    factor_level_uri=factor_level_uri, 
    germplasm_uri=germplasm_uri
)
print(df.head())
```
#### Explanation:

- **factor_level_uri**: Filters scientific objects based on the specified factor level (e.g., temperature, humidity).
- **germplasm_uri**: Filters based on the exact URI of the germplasm.
  **`Important Note`**: The germplasm URI filter only applies to the lowest level of the germplasm hierarchy. For example:
  - If the germplasm URI corresponds to a Species level, it will only filter scientific objects of type `Species`.
  - If the germplasm URI corresponds to a Variety or Accession level, the filter applies only to that specific germplasm type.



## 4. Filtering by Factor Level names 

In this example, the filter is applied based on the **factor levels** provided. The user filters the scientific objects based on the names of the factor levels.

```python
from package.exceptions.custom_exceptions import APIRequestError
from package.experiment.ls_scientific_objects import get_os_by_exp

# Assuming `session` is already defined with authentication details
experiment = "ZA17_2017_03_30"  # Replace with the actual experiment ID
obj_type = "http://www.opensilex.org/vocabulary/oeso#Plant"  # Replace with the actual object type URI
df = get_os_by_exp(
    session, 
    experiment, 
    obj_type, 
    factor_levels=["Factor1.Level1", "Factor2.Level1"],  # Filter by specific factor levels
)
print(df.head())
```
#### Explanation:

- **factor_levels**: Filters the scientific objects based on the specific names of factor and factor levels (e.g., `Factor1.Level1`, `Factor2.Level2`, etc.).  
  This example will return all scientific objects that match the specified factor levels (`Factor1.Level1`, `Factor2.Level1`).

## Expected Output:
The function will return a pandas DataFrame containing the scientific objects related to the specified experiment and object type, including details like uri, name, type, and associated factor levels and germplasm information. The data will also be saved in a CSV file named scientific_objects.csv inside the temp_files directory.


### Directory Structure for CSV File:
```txt
project_root/
    ├── temp_files/
        └── scientific_objects.csv
```
## Error Handling
### APIRequestError:
If any GraphQL request fails (e.g., due to a malformed request, connection issues, or server errors), an APIRequestError will be raised, providing details about the error.