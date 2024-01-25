import os
import typing as t

import requests

from . import schema
from .utils import compact_mapping
from .exceptions import NeonClientException


__VERSION__ = "0.1.0"

NEON_API_KEY_ENVIRON = "NEON_API_KEY"
NEON_API_BASE_URL = "https://console.neon.tech/api/v2/"
ENABLE_PYDANTIC = True


def returns_model(model, is_array=False):
    """Decorator that returns a model instance."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            if not ENABLE_PYDANTIC:
                return func(*args, **kwargs)

            if is_array:
                return [model(**item) for item in func(*args, **kwargs)]
            else:
                return model(**func(*args, **kwargs))

        return wrapper

    return decorator


def returns_subkey(key):
    """Decorator that returns a subkey."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return getattr(func(*args, **kwargs), key)
            except AttributeError:
                return func(*args, **kwargs)[key]

        return wrapper

    return decorator


class NeonAPI:
    def __init__(self, api_key: str, *, base_url: str = None):
        """A Neon API client."""

        # Set the base URL.
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

        return r.json()

    def url_join(self, *args):
        """Join multiple URL path components."""

        return "/".join(args)

    @classmethod
    def from_environ(cls):
        """Create a new Neon API client from the `NEON_API_KEY` environment variable."""

        return cls(os.environ[NEON_API_KEY_ENVIRON])

    @returns_model(schema.CurrentUserInfoResponse)
    def me(self) -> t.Dict[str, t.Any]:
        """Get the current user."""
        return self.request("GET", "users/me")

    @returns_model(schema.ApiKeysListResponseItem, is_array=True)
    def api_keys(self) -> t.List[t.Dict[str, t.Any]]:
        """Get a list of API keys."""
        return self.request("GET", "api_keys")

    @returns_model(schema.ApiKeyCreateResponse)
    def api_key_create(self, **json: dict) -> t.Dict[str, t.Any]:
        """Create a new API key."""
        return self.request("POST", "api_keys", json=json)

    @returns_model(schema.ApiKeyRevokeResponse)
    def api_key_revoke(self, api_key_id: str) -> t.Dict[str, t.Any]:
        """Revoke an API key.

        :param api_key_id: The ID of the API key to revoke.
        :return: A dictionary representing the API key.
        """
        return self.request("DELETE", f"api_keys/{ api_key_id }")

    # @returns_subkey("projects")
    @returns_model(schema.ProjectsResponse)
    def projects(
        self,
        *,
        shared: bool = False,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> t.List[t.Dict[str, t.Any]]:
        """Get a list of projects. If shared is True, get a list of shared projects.

        :param shared: Whether to retrieve shared projects (default is False).
        :param cursor: The cursor for pagination (default is None).
        :param limit: The maximum number of projects to retrieve (default is None).
        :return: A list of dictionaries representing the projects.
        """

        r_path = "projects" if not shared else "projects/shared"
        r_params = compact_mapping({"cursor": cursor, "limit": limit})

        return self.request("GET", r_path, params=r_params)

    @returns_model(schema.ProjectResponse)
    def project(self, project_id: str) -> t.Dict[str, t.Any]:
        """Get a project."""

        r_path = self.url_join("projects", project_id)

        return self.request(
            "GET",
            r_path,
        )

    @returns_model(schema.ProjectResponse)
    def project_create(self, **json: dict) -> t.Dict[str, t.Any]:
        """Create a new project. Accepts all keyword arguments for json body."""

        return self.request("POST", "projects", json=json)

    @returns_model(schema.ProjectResponse)
    def project_update(self, project_id: str, **json: dict) -> t.Dict[str, t.Any]:
        """Updates a project. Accepts all keyword arguments for json body."""

        return self.request("PATCH", f"projects/{ project_id }", json=json)

    @returns_model(schema.ProjectResponse)
    def project_delete(self, project_id: str) -> t.Dict[str, t.Any]:
        """Delete a project."""

        return self.request("DELETE", f"projects/{ project_id }")

    @returns_model(schema.BranchesResponse)
    def branches(
        self,
        project_id: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> t.Dict[str, t.Any]:
        """Get a list of branches."""

        # Construct the request path and parameters.
        r_path = self.url_join("projects", project_id, "branches")
        r_params = compact_mapping({"cursor": cursor, "limit": limit})

        # Make the request.
        return self.request("GET", r_path, params=r_params)

    @returns_model(schema.BranchResponse)
    def branch(self, project_id: str, branch_id: str) -> t.Dict[str, t.Any]:
        """Get a branch."""

        # Construct the request path.
        r_path = self.url_join("projects", project_id, "branches", branch_id)

        # Make the request.
        return self.request("GET", r_path)

    @returns_model(schema.BranchOperations)
    def branch_create(self, project_id: str, **json: dict) -> t.Dict[str, t.Any]:
        """Create a new branch. Accepts all keyword arguments for json body."""
        return self.request("POST", f"projects/{ project_id }/branches", json=json)

    @returns_model(schema.BranchOperations)
    def branch_update(
        self, project_id: str, branch_id: str, **json: dict
    ) -> t.Dict[str, t.Any]:
        """Update a branch by branch_id. Accepts all keyword arguments for json body."""

        return self.request(
            "PATCH", f"projects/{ project_id }/branches/{ branch_id }", json=json
        )

    @returns_model(schema.BranchOperations)
    def branch_delete(self, project_id: str, branch_id: str) -> t.Dict[str, t.Any]:
        """Delete a branch by branch_id."""
        return self.request("DELETE", f"projects/{ project_id }/branches/{ branch_id }")

    @returns_model(schema.BranchOperations)
    def branch_set_as_primary(
        self, project_id: str, branch_id: str
    ) -> t.Dict[str, t.Any]:
        """Set a branch as primary by branch_id."""

        return self.request(
            "POST", f"projects/{ project_id }/branches/{ branch_id }/set_as_primary"
        )

    @returns_model(schema.DatabasesResponse)
    def databases(
        self,
        project_id: str,
        branch_id: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> t.Dict[str, t.Any]:
        """Get a list of databases."""

        # Construct the request path and parameters.
        r_path = self.url_join(
            "projects", project_id, "branches", branch_id, "databases"
        )
        r_params = compact_mapping({"cursor": cursor, "limit": limit})

        # Make the request.
        return self.request("GET", r_path, params=r_params)

    @returns_model(schema.DatabaseResponse)
    def database(
        self, project_id: str, branch_id: str, database_id: str
    ) -> t.Dict[str, t.Any]:
        """Get a database."""

        # Construct the request path.
        r_path = self.url_join(
            "projects", project_id, "branches", branch_id, "databases", database_id
        )

        # Make the request.
        return self.request("GET", r_path)

    @returns_model(schema.DatabaseResponse)
    def database_create(
        self, project_id: str, branch_id: str, **json: dict
    ) -> t.Dict[str, t.Any]:
        """Create a new database. Accepts all keyword arguments for json body."""

        return self.request(
            "POST",
            f"projects/{ project_id }/branches/{ branch_id }/databases",
            json=json,
        )

    @returns_model(schema.DatabaseResponse)
    def database_update(
        self, project_id: str, branch_id: str, database_id: str, **json: dict
    ) -> t.Dict[str, t.Any]:
        """Update a database. Accepts all keyword arguments for json body."""

        return self.request(
            "PUT",
            f"projects/{ project_id }/branches/{ branch_id }/databases/{ database_id }",
            json=json,
        )

    @returns_model(schema.DatabaseResponse)
    def database_delete(
        self, project_id: str, branch_id: str, database_id: str
    ) -> t.Dict[str, t.Any]:
        """Delete a database by database_id."""

        return self.request(
            "DELETE",
            f"projects/{ project_id }/branches/{ branch_id }/databases/{ database_id }",
        )

    @returns_model(schema.EndpointsResponse)
    def endpoints(self, project_id: str) -> t.Dict[str, t.Any]:
        """Get a list of endpoints for a given branch."""
        return self.request("GET", f"projects/{ project_id }/endpoints")

    @returns_model(schema.EndpointResponse)
    def endpoint(self, project_id: str, endpoint_id: str) -> t.Dict[str, t.Any]:
        """Get an endpoint for a given branch."""
        return self.request(
            "GET",
            f"projects/{ project_id }/endpoints/{ endpoint_id }",
        )

    @returns_model(schema.EndpointOperations)
    def endpoint_create(
        self,
        project_id: str,
        **json: dict,
    ) -> t.Dict[str, t.Any]:
        """Create a new endpoint. Accepts all keyword arguments for json body."""

        return self.request("POST", f"projects/{ project_id }/endpoints", json=json)

    @returns_model(schema.EndpointOperations)
    def endpoint_delete(self, project_id: str, endpoint_id: str) -> t.Dict[str, t.Any]:
        """Delete an endpoint by endpoint_id."""

        return self.request(
            "DELETE",
            f"projects/{ project_id }/endpoints/{ endpoint_id }",
        )

    @returns_model(schema.EndpointOperations)
    def endpoint_update(
        self, project_id: str, endpoint_id: str, **json: dict
    ) -> t.Dict[str, t.Any]:
        """Update an endpoint. Accepts all keyword arguments for json body."""

        return self.request(
            "PATCH",
            f"projects/{ project_id }/endpoints/{ endpoint_id }",
            json=json,
        )

    @returns_model(schema.EndpointOperations)
    def endpoint_start(self, project_id: str, endpoint_id: str):
        """Start an endpoint by endpoint_id."""

        return self.request(
            "POST",
            f"projects/{ project_id }/endpoints/{ endpoint_id }/start",
        )

    @returns_model(schema.EndpointOperations)
    def endpoint_suspend(self, project_id: str, endpoint_id: str):
        """Suspend an endpoint by endpoint_id."""

        return self.request(
            "POST",
            f"projects/{ project_id }/endpoints/{ endpoint_id }/suspend",
        )

    @returns_model(schema.RolesResponse)
    def roles(self, project_id: str, branch_id: str) -> t.Dict[str, t.Any]:
        """Get a list of roles for a given branch."""
        return self.request(
            "GET", f"projects/{ project_id }/branches/{ branch_id }/roles"
        )

    @returns_model(schema.RoleResponse)
    def role(
        self, project_id: str, branch_id: str, role_name: str
    ) -> t.Dict[str, t.Any]:
        """Get a role for a given branch."""
        return self.request(
            "GET", f"projects/{ project_id }/branches/{ branch_id }/roles/{ role_name }"
        )

    @returns_model(schema.RoleOperations)
    def role_create(
        self,
        project_id: str,
        branch_id: str,
        role_name: str,
    ) -> t.Dict[str, t.Any]:
        """Create a new role. Accepts all keyword arguments for json body."""

        return self.request(
            "POST",
            f"projects/{ project_id }/branches/{ branch_id }/roles",
            json={"role": {"name": role_name}},
        )

    @returns_model(schema.RoleOperations)
    def role_delete(
        self,
        project_id: str,
        branch_id: str,
        role_name: str,
    ) -> t.Dict[str, t.Any]:
        """Delete a role by given role name."""

        return self.request(
            "DELETE",
            f"projects/{ project_id }/branches/{ branch_id }/roles/{ role_name }",
        )

    @returns_model(schema.RolePasswordResponse)
    def role_password_reveal(
        self,
        project_id: str,
        branch_id: str,
        role_name: str,
    ) -> t.Dict[str, t.Any]:
        """Get a role password."""

        return self.request(
            "POST",
            f"projects/{ project_id }/branches/{ branch_id }/roles/{ role_name }/reveal_password",
        )

    @returns_model(schema.RoleOperations)
    def role_password_reset(
        self,
        project_id: str,
        branch_id: str,
        role_name: str,
    ) -> t.Dict[str, t.Any]:
        """Reset a role password."""

        return self.request(
            "POST",
            f"projects/{ project_id }/branches/{ branch_id }/roles/{ role_name }/reset_password",
        )

    @returns_model(schema.OperationsResponse)
    def operations(
        self,
        project_id: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> t.Dict[str, t.Any]:
        """Get a list of operations."""

        r_params = compact_mapping({"cursor": cursor, "limit": limit})
        return self.request(
            "GET", f"projects/{ project_id }/operations", params=r_params
        )

    @returns_model(schema.OperationResponse)
    def operation(self, project_id: str, operation_id: str) -> t.Dict[str, t.Any]:
        """Get an operation."""
        return self.request(
            "GET", f"projects/{ project_id }/operations/{ operation_id }"
        )
