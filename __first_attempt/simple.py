import os

import requests
from requests.exceptions import HTTPError
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder

from . import models
from .client import ItemView, CollectionView
from .exceptions import NeonClientException
from .__version__ import __version__
from .resources import PagedOperationsResponse, PagedProjectsResponse
from .utils import squash

NEON_ENVIRON_NAME = "NEON_API_KEY"


class NeonClient:
    def __init__(
        self, api_key: str, *, base_url: str = "https://console.neon.tech/api/v2/"
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.user_agent = f"neon-client/{__version__}"

    @classmethod
    def from_environ(cls, environ=os.environ.copy(), **kwargs):
        """Create a new NeonClient instance from environment variables.

        Args:
            environ (dict, optional): The environment variables to use. Defaults to os.environ.copy().
            **kwargs: Additional keyword arguments to be passed to the NeonClient constructor.

        Returns:
            NeonClient: The new NeonClient instance.
        """
        return cls(environ[NEON_ENVIRON_NAME], **kwargs)

    def url_join(self, *args):
        """Join URL path segments.

        Args:
            *args: The path segments to join.

        Returns:
            str: The joined path.
        """
        return "/".join(args)

    def request(
        self,
        method: str,
        path: str,
        data: dict | None = None,
        *,
        request_model: BaseModel | None = None,
        response_model: BaseModel | None = None,
        response_is_array=False,
        check_status_code=True,
        _debug=False,
        **kwargs,
    ):
        """
        Sends an HTTP request to the specified path using the specified method.

        Args:
            method (str): The HTTP method to use for the request.
            path (str): The path to send the request to.
            request_model (BaseModel, optional): The model to serialize the request body from. Defaults to None.
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
            except requests.exceptions.HTTPError:
                raise NeonClientException(r.text)

        if response_model:
            if response_is_array:
                # Shortcut for when the response is a list of items.
                if type(response_is_array) == "str":
                    response_parsed = [
                        response_model.model_construct(**item)
                        for item in r.json()[response_is_array]
                    ]
                elif response_is_array is True:
                    response_parsed = [
                        response_model.model_construct(**item) for item in r.json()
                    ]
            else:
                response_parsed = response_model.model_construct(**r.json())

            if _debug:
                print(r, r.json())

            return response_parsed
        else:
            return r

    def me(self):
        return self.request(
            method="GET",
            path=self.url_join("users", "me"),
            response_model=models.CurrentUserInfoResponse,
        )

    def api_keys(self):
        """Get a list of API keys."""
        r = self.request(
            method="GET",
            path="api_keys",
            response_model=models.ApiKeysListResponseItem,
            response_is_array=True,
            _debug=True,
        )
        return CollectionView(r, key_ids=["id", "name"])

    def projects(
        self,
        *,
        cursor: int | None = None,
        limit: int | None = None,
        shared: bool = False,
    ):
        """Get a list of projects."""

        # Pagination support.
        projects_params = squash({"cursor": cursor, "limit": limit})

        r = self.request(
            method="GET",
            path=(self.api.url_join("projects", "shared") if shared else "projects"),
            params=projects_params,
            response_model=PagedProjectsResponse,
        )

        return CollectionView(r, key_ids=["id", "name"], collection_id="projects")
