from requests.exceptions import HTTPError


class NeonAPIError(HTTPError):
    pass
