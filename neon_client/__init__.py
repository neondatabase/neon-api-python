from .client import NeonAPI


def from_environ():
    return NeonAPI.from_environ()


def from_token(token):
    return NeonAPI.from_token(token)


from .client import *
