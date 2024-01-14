from typing import List
import requests
from pydantic import BaseModel

from .openapi_models import *
from .exceptions import NeonClientException
from .__version__ import __version__


class Neon_API_V2:
    def __init__(
        self, api_key: str, *, base_url: str = "https://console.neon.tech/api/v2/"
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.user_agent = f"neon-client/{__version__}"

    def request(
        self,
        method: str,
        path: str,
        *,
        response_model: BaseModel = None,
        response_is_array=False,
        check_status_code=True,
        **kwargs,
    ):
        """
        Sends an HTTP request to the specified path using the specified method.

        Args:
            method (str): The HTTP method to use for the request.
            path (str): The path to send the request to.
            response_model (BaseModel, optional): The model to deserialize the response into. Defaults to None.
            response_is_array (bool or str, optional): Indicates whether the response is a list of items. If a string is provided, it is used as the key to access the list in the response JSON. Defaults to False.
            check_status_code (bool, optional): Indicates whether to check the status code of the response and raise an exception if it is not successful. Defaults to True.
            **kwargs: Additional keyword arguments to be passed to the request.

        Returns:
            The deserialized response if a response model is provided, otherwise the raw response object.
        """
        # Set HTTP headers for outgoing requests.
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.api_key}"
        headers["Accept"] = "application/json"
        headers["Content-Type"] = "application/json"
        headers["User-Agent"] = self.user_agent

        r = self.session.request(
            method, self.base_url + path, headers=headers, **kwargs
        )

        if check_status_code:
            # TODO: add custom exception classes here.
            try:
                r.raise_for_status()
            except:
                raise NeonClientException(r.text)

        if response_model:
            if response_is_array:
                # Shortcut for when the response is a list of items.
                if type(response_is_array) == "str":
                    return [
                        response_model(**item) for item in r.json()[response_is_array]
                    ]
                elif response_is_array == True:
                    return [response_model(**item) for item in r.json()]
            else:
                return response_model(**r.json())
        else:
            return r

    def url_join(self, *args):
        """Join the specified path components into a URL."""
        return "/".join(args)
