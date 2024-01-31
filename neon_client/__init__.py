from .client import NeonAPI
from .__version__ import __version__


def from_environ():
    return NeonAPI.from_environ()


def from_token(token):
    return NeonAPI.from_token(token)


from .client import *
