import os
import typing as t

import requests
from pydantic import BaseModel, ValidationError

from . import schema
from .utils import compact_mapping
from .exceptions import NeonClientException

from fastapi.encoders import jsonable_encoder


__VERSION__ = "0.1.0"

NEON_API_KEY_ENVIRON = "NEON_API_KEY"
NEON_API_BASE_URL = "https://console.neon.tech/api/v2/"


class NeonResource:
    def __init__(self, client, obj, data_model: BaseModel):
        """A Neon Resource.  Used to wrap API responses, and deserialize them.

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
        """The object in question."""

        if self._data_model:
            # Cache the object.
            if not self.__cached_obj:
                # Deserialize the object. Fallback to the model constructor if the
                # data model is not a Pydantic model.
                self.__cached_obj = self._data_model(**self._data)
                # try:
                #     self.__cached_obj = self._data_model(**self._data)
                # except ValidationError:
                #     self.__cached_obj = self._data_model.model_construct(**self._data)

            # Return the cached object.
            return self.__cached_obj
        else:
            # Return the raw data.
            return self._data

    def __getattribute__(self, name):
        """Get an attribute from the object."""

        try:
            # Try to get the attribute from this object.
            return super().__getattribute__(name)
        except AttributeError:
            # Try to get the attribute from the object data.
            return getattr(self.obj, name)

    def __getitem__(self, key):
        """Get an item from the object."""

        return getattr(self.obj, key, None) or self.obj[key]

    def __repr__(self):
        """Return a string representation."""

        return repr(self.obj)


class APIKey(NeonResource):
    """A Neon API key."""

    @classmethod
    def create(cls, client, key_name: str):
        """Create a new API key."""

        obj = schema.ApiKeyCreateRequest(key_name=key_name)
        r = client.request("POST", "api_keys", json=jsonable_encoder(obj))

        return cls(client=client, obj=r, data_model=schema.ApiKeyCreateResponse)

    @classmethod
    def get_list(cls, client):
        """Get a list of API keys."""

        obj = client.request("GET", "api_keys")
        return [
            cls(client=client, obj=obj, data_model=schema.ApiKeysListResponseItem)
            for obj in obj
        ]

    @classmethod
    def revoke_with_id(cls, client, api_key_id):
        """Revoke an API key, via object instance."""

        obj = client.request("DELETE", f"api_keys/{ api_key_id }")

        return cls(client=client, obj=obj, data_model=schema.ApiKeyRevokeResponse)

    def revoke(self):
        """Revoke the API key."""

        return self.revoke_with(self._client, self.id)


class User(NeonResource):
    """A Neon user."""

    @classmethod
    def get_current_user_info(cls, client):
        """Get the current user."""

        # Make the Request.
        r = client.request("GET", "users/me")

        # Deserialize the response.
        return cls(
            client=client,
            obj=r,
            data_model=schema.CurrentUserInfoResponse,
        )


class Project(NeonResource):
    @classmethod
    def get_list(
        cls,
        client,
        *,
        shared: bool = False,
        cursor: str | None = None,
        limit: int | None = None,
    ):
        """Get a list of projects."""

        r_path = "projects" if not shared else "projects/shared"
        r_params = compact_mapping({"cursor": cursor, "limit": limit})

        r = client.request("GET", r_path, params=r_params)

        return [
            cls(client=client, obj=obj, data_model=schema.ProjectListItem)
            for obj in r["projects"]
        ]

    @classmethod
    def get(cls, client, project_id: str):
        """Get a project."""

        r_path = client.url_join("projects", project_id)
        r = client.request(
            "GET",
            r_path,
            response_model=schema.ProjectResponse,
        )

        return cls(
            client=client,
            obj=r.project,
            data_model=schema.ProjectListItem,
        )

    @classmethod
    def create(cls, client, **json: dict):
        """Create a new project. Accepts all keyword arguments from ProjectCreateRequest."""

        r = client.request("POST", "projects", json=jsonable_encoder(json))

        return cls(
            client=client,
            obj=r,
            data_model=schema.ProjectResponse,
        )

    @classmethod
    def delete_with_id(cls, client, project_id: str):
        """Delete a project."""

        r = client.request("DELETE", f"projects/{ project_id }")

        return cls(
            client=client,
            obj=r,
            data_model=schema.ProjectResponse,
        )

    def delete(self):
        """Delete the project."""

        return self.delete_with_id(self._client, self.id)


class Branch(NeonResource):
    @classmethod
    def list(
        cls,
        client,
        project_id: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ):
        """Get a list of branches."""

        # Construct the request path and parameters.
        r_path = "/".join(["projects", project_id, "branches"])
        r_params = compact_mapping({"cursor": cursor, "limit": limit})

        # Make the request.
        r = client.request("GET", r_path, params=r_params)

        # Deserialize the response.
        return [
            cls(client=client, obj=obj, data_model=schema.ProjectListItem)
            for obj in r["branches"]
        ]

    @classmethod
    def get(cls, client, project_id: str, branch_id: str):
        """Get a list of branches."""

        # Construct the request path.
        r_path = client.url_join("projects", project_id, "branches", branch_id)

        # Make the request.
        obj = client.request("GET", r_path, response_model=schema.ProjectResponse)

        # Deserialize the response.
        return cls(
            client=client, obj=jsonable_encoder(obj.branch), data_model=schema.Project
        )

    @classmethod
    def create(
        cls,
        client,
        project_id: str,
        *,
        endpoints: t.List[schema.BranchCreateRequestEndpointOptions] | None = None,
        branch: schema.Branch2 | None = None,
        **kwargs,
    ):
        """Create a new branch."""

        # Construct the request object.
        kwargs.setdefault("endpoints", endpoints)
        kwargs.setdefault("branch", branch)

        # Validate and prepare the request body.
        obj = schema.BranchCreateRequest(**kwargs)

        # Make the request.
        r_path = client.url_join("projects", project_id, "branches")

        # Skip the request body if there are no endpoints or branch.
        if obj.endpoints or obj.branch:
            r = client.request("POST", r_path, json=jsonable_encoder(obj))
        else:
            r = client.request("POST", r_path)

        return cls(client=client, obj=r, data_model=schema.BranchResponse)

    @classmethod
    def get_connection_string(cls, client, project_id: str, branch_id: str):
        """Get a connection string for a branch."""

        # Construct the request path.
        r_path = client.url_join(
            "projects", project_id, "branches", branch_id, "connection_string"
        )

        # Make the request.
        obj = client.request(
            "GET", r_path, response_model=schema.BranchConnectionStringResponse
        )

        # Deserialize the response.
        return obj.connection_string


class Operation(NeonResource):
    @classmethod
    def list(
        cls,
        client,
        project_id: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ):
        """Get a list of operations."""

        # Construct the request path and parameters.
        r_path = client.url_join("projects", project_id, "operations")
        r_params = compact_mapping({"cursor": cursor, "limit": limit})

        # Make the request.
        obj = client.request(
            "GET", r_path, params=r_params, response_model=schema.OperationsResponse
        )

        # Deserialize the response.
        return [
            cls(client=client, obj=o, data_model=schema.Operation)
            for o in obj.operations
        ]

    @classmethod
    def get(
        cls,
        client,
        project_id: str,
        operation_id: str,
    ):
        """Get a list of operations."""

        # Construct the request path and parameters.
        r_path = client.url_join("projects", project_id, "operations", operation_id)

        # Make the request.
        obj = client.request("GET", r_path, response_model=schema.OperationResponse)

        # Deserialize the response.
        return cls(client=client, obj=obj.operation, data_model=schema.Operation)


class NeonAPI:
    def __init__(self, api_key: str, *, base_url=None):
        """A Neon API client."""

        if not base_url:
            base_url = NEON_API_BASE_URL

        # Private attributes.
        self._api_key = api_key
        self._session = requests.Session()

        # Public attributes.
        self.base_url = base_url
        self.user_agent = f"neon-client/python version=({__VERSION__})"

    def __repr__(self):
        return f"<NeonAPI base_url={self.base_url!r}>"

    def request(
        self,
        method: str,
        path: str,
        response_model: BaseModel | None = None,
        **kwargs,
    ):
        """Send an HTTP request to the specified path using the specified method."""

        # Set HTTP headers for outgoing requests.
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self._api_key}"
        headers["Accept"] = "application/json"
        headers["Content-Type"] = "application/json"
        headers["User-Agent"] = self.user_agent

        # Send the request.
        r = self._session.request(
            method, self.base_url + path, headers=headers, **kwargs
        )

        # Check the response status code.
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            raise NeonClientException(r.text)

        # Deserialize the response.
        if response_model:
            return response_model.model_construct(**r.json())
        else:
            return r.json()

    def url_join(self, *args):
        """Join multiple URL path components."""

        return "/".join(args)

    @classmethod
    def from_environ(cls):
        """Create a new Neon API client from the NEON_API_KEY environment variable."""

        return cls(os.environ[NEON_API_KEY_ENVIRON])

    def me(self):
        """Get the current user."""
        return User.get_current_user_info(client=self)

    def api_keys(self):
        """Get a list of API keys."""
        return APIKey.get_list(client=self)

    def projects(self, *, shared: bool = False, **kwargs):
        """Get a list of projects."""
        return Project.get_list(client=self, shared=shared, **kwargs)

    def project(self, project_id: str):
        """Get a project."""
        return Project.get(client=self, project_id=project_id)

    def branches(self, project_id: str):
        """Get a list of branches."""
        return Branch.list(client=self, project_id=project_id)

    def operations(self, project_id: str):
        """Get a list of operations."""
        return Operation.list(client=self, project_id=project_id)

    def operation(self, project_id: str, operation_id: str):
        """Get an operation."""
        return Operation.get(
            client=self, project_id=project_id, operation_id=operation_id
        )
