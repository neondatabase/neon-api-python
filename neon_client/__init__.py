from .client import NeonAPI
from .__version__ import __version__
from .exceptions import NeonAPIError


def from_environ():
    """Create a NeonAPI instance from environment variables."""

    return NeonAPI.from_environ()


def from_token(token):
    """Create a NeonAPI instance from a token."""

    return NeonAPI.from_token(token)
