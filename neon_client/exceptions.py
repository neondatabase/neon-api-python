from requests.exceptions import HTTPError


class NeonClientException(HTTPError):
    pass
