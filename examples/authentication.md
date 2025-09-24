# Documentation of `login` function

## Description

The `login` function authenticates a user with an OpenSILEX server using the provided credentials and server URLs. It returns an authentication token along with headers and URLs for both REST and GraphQL APIs, which can be used for further requests. The function checks if all required parameters are provided and validates the server URLs, ensuring that the authentication process is secure. If the authentication fails, it raises an `AuthenticationError`.

## Arguments

- **username (str)**:  
  - The email address of the user to authenticate.

- **password (str)**:  
  - The password of the user for authentication.

- **instance_rest (str)**:  
  - The URL of the REST API instance. This can be a local or remote server URL.

- **url_graphql (str)**:  
  - The URL of the GraphQL API instance. This can also be a local or remote server URL.

## Returns

- **dict**:  
  - A dictionary containing the following keys:
    - `token` *(str)*: The authentication token for subsequent API requests.
    - `url_rest` *(str)*: The full URL of the REST API.
    - `url_graphql` *(str)*: The full URL of the GraphQL API.
    - `headers_graphql` *(dict)*: The headers for GraphQL requests, including the authorization token.
    - `headers_rest` *(dict)*: The headers for REST requests, including the authorization token.

## Example Usage

```python
from package.auth.auth import login

# Define the user credentials and server details
username = "admin@opensilex.org"
password = "mysecurepassword"
instance_rest = "http://138.102.159.36:8084/demo/rest"  # REST API instance
url_graphql = "http://138.102.159.37/graphql"  # GraphQL API instance

# Perform authentication
session = login(
    username=username,
    password=password,
    instance_rest=instance_rest,
    url_graphql=url_graphql
)

# Output the authentication token
print(session["token"])
```

## Expected Output
```bash
<authentication_token>
```

### Explanation:

- Headers:

    The function will generate headers for both the REST and GraphQL APIs, each including the authentication token in the format Bearer <token>.

## Error Handling 
### ValueError: Missing or Empty Parameters

If any of the required parameters (username, password, instance_rest, or url_graphql) are missing or empty, a ValueError will be raised. For example, if the password is left empty:

```python
from package.auth.auth import login
from package.exceptions.custom_exceptions import AuthenticationError

try:
    session = login(
        username="admin@opensilex.org",
        password="",  # Empty password
        instance_rest="http://localhost/rest",
        url_graphql="http://localhost/graphql"
    )
except ValueError as e:
    print(f"Error: {e}")
```
## Expected Output for Missing/Empty Password:
```text
Error: Tous les paramètres (nom d'utilisateur, mot de passe, instance REST, et URL GraphQL) sont requis.
```