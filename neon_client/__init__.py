from .client import NeonAPI
from .__version__ import __version__
from .exceptions import NeonAPIError


def from_environ():
    return NeonAPI.from_environ()


def from_token(token):
    return NeonAPI.from_token(token)
