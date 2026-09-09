# exceptions.py

class AuthenticationError(Exception):
    """Exception raised for errors in the authentication process."""
    pass

class APIRequestError(Exception):
    """Exception raised for errors during API requests."""
    pass