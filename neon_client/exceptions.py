from requests.exceptions import HTTPError


class NeonAPIException(HTTPError):
    pass
