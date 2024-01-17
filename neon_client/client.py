import os
from collections.abc import Sequence

import requests
from pydantic import BaseModel, ValidationError

from .jsonschema import (
    ApiKeysListResponseItem,
    ApiKeyCreateRequest,
    ApiKeyCreateResponse,
    ApiKeyRevokeResponse,
)
from .jsonschema import CurrentUserInfoResponse


__VERSION__ = "0.1.0"

NEON_API_KEY_ENVIRON = "NEON_API_KEY"
NEON_API_BASE_URL = "https://console.neon.tech/api/v2/"


class NeonClientException(requests.exceptions.HTTPError):
    pass


class APIKey:
    """A Neon API key."""

    def __init__(
        self,
        client,
        obj,
        data_model: BaseModel,
        **kwargs,
    ):
        """A Neon API key.

        Args:
            client (NeonAPI): The Neon API client.
            obj (dict): The API key data.
            data_model (BaseModel, optional): The data model to use for deserialization. Defaults to None.
        """
        self._client = client
        self._data = obj
        self._data_model = data_model
        self.__cached_obj = None

    @property
    def obj(self):
        if not self.__cached_obj:
            self.__cached_obj = self._data_model(**self._data)

        return self.__cached_obj

    def __repr__(self):
        return repr(self.obj)

    @classmethod
    def create(cls, client, key_name: str):
        """Create a new API key."""

        obj = ApiKeyCreateRequest(key_name=key_name)
        r = client.request("POST", "api_keys", json=obj.model_dump())
        return cls(
            client=client,
            obj=r,
            data_model=ApiKeyCreateResponse,
        )

        # ApiKeyCreateResponse(**r)

    @classmethod
    def list(cls, client):
        """Get a list of API keys."""

        r = client.request("GET", "api_keys")
        return [
            cls(client=client, obj=x, data_model=ApiKeysListResponseItem) for x in r
        ]

    @classmethod
    def revoke(cls, client, api_key):
        """Revoke an API key."""

        r = client.request("DELETE", f"api_keys/{ api_key.obj.id }")
        return cls(client=client, obj=r, data_model=ApiKeyRevokeResponse)


class NeonAPI:
    def __init__(self, api_key, *, base_url=None):
        if not base_url:
            base_url = NEON_API_BASE_URL

        # Private attributes.
        self._api_key = api_key
        self._session = requests.Session()

        # Public attributes.
        self.base_url = base_url
        self.user_agent = f"neon-client/{__VERSION__}"

    def request(self, method, path, **kwargs):
        """Send an HTTP request to the specified path using the specified method."""
        # Set HTTP headers for outgoing requests.
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self._api_key}"
        headers["Accept"] = "application/json"
        headers["Content-Type"] = "application/json"
        headers["User-Agent"] = self.user_agent

        r = self._session.request(
            method, self.base_url + path, headers=headers, **kwargs
        )
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            raise NeonClientException(r.text)

        return r.json()

    @classmethod
    def from_environ(cls):
        """Create a new Neon API client from the NEON_API_KEY environment variable."""

        return cls(os.environ[NEON_API_KEY_ENVIRON])
