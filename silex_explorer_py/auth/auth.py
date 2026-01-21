import requests
from silex_explorer_py.exceptions.custom_exceptions import AuthenticationError
from silex_explorer_py.uri_name_manager.uri_name_table import init_uri_name

def login(username, password, instance_rest, url_graphql):
    """
    Authenticate with the OpenSILEX server and return authentication details, 
    and initialize the URI-Name table.

    This function authenticates a user with an OpenSILEX server using REST API 
    and returns a token along with URLs and headers required for subsequent requests.
    Additionally, after a successful login, it initializes the global URI-Name table 
    (using the `init_uri_name` function).

    Args:
        username (str): The email address of the user.
        password (str): The user's password.
        instance_rest (str): Base URL of the REST API instance. 
        url_graphql (str): Base URL for the GraphQL API instance.
    Returns:
        dict: A dictionary containing the following keys:
            - `token` (str): The authentication token.
            - `url_rest` (str): Full URL of the REST API.
            - `url_graphql` (str): Full URL of the GraphQL API.
            - `headers_graphql` (dict): Headers for GraphQL requests.
            - `headers_rest` (dict): Headers for REST requests.

    Raises:
        AuthenticationError: If authentication fails due to invalid credentials or other server issues.
        requests.exceptions.RequestException: If there is a network issue during the request.

    Example:
        ```python
        from package.auth.auth import login

        session = login(
            username="admin@opensilex.org",
            password="mysecurepassword",
            instance_rest="http://138.102.159.36:8084/demo/rest",
            url_graphql="http://138.102.159.37/graphql"
        )
        print(session["token"])
        ```
        
    Additional Notes:
        - After a successful login, the `uri_name` table is initialized (either loaded from a CSV if it exists or created as an empty DataFrame).
        - The `uri_name` table is ready to be used in subsequent operations immediately after the login process.
        
    """
    # Check that all parameters are provided and not empty
    if not all([username, password, instance_rest, url_graphql]):
        raise ValueError("Tous les paramètres (nom d'utilisateur, mot de passe, instance REST, et URL GraphQL) sont requis.")

    # Remove any trailing slashes from the instance URLs
    url_rest = instance_rest.rstrip("/")
    url_graphql = url_graphql.rstrip("/")

    # Define the authentication route directly in the function
    auth_route = "/security/authenticate"

    # Prepare the authentication URL and the request body
    auth_url = f"{url_rest}{auth_route}"
    credentials = {"identifier": username, "password": password}

    try:
        # Send a POST request to authenticate
        response = requests.post(auth_url, json=credentials)

        # Check if authentication was successful
        if 200 <= response.status_code < 300:
            json_response = response.json()
            token = json_response['result']['token']

            # Construct headers for GraphQL and REST requests using the token
            headers_graphql = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
            }

            headers_rest = {
                "Authorization": f'Bearer {token}'
            }

            # Initialize the uri_name table after successful authentication
            init_uri_name(save=True) 
             
            # Return a dictionary with the token, instance, URLs, and headers
            return {
                "token": token,
                "url_rest": url_rest,
                "url_graphql": url_graphql,
                "headers_graphql": headers_graphql,
                "headers_rest": headers_rest
            }
        else:
             # Here we handle the failed authentication more gracefully
            response_json = response.json()
            # Extract the specific error message from the response JSON
            error_message = response_json.get('result', {}).get('message', 'Unknown authentication error.')
            raise AuthenticationError(f"Authentication failed: {error_message}")

    except requests.exceptions.RequestException as e:
        raise AuthenticationError(f"An error occurred during authentication: {e}")
