from requests.exceptions import HTTPError


class NeonClientException(HTTPError):
    """Base exception class for all exceptions raised by the Neon Client."""

    pass


class NeonClientAuthenticationException(NeonClientException):
    """Exception raised when authentication fails."""

    pass
