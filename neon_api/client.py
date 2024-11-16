import os
import typing as t
from datetime import datetime
from functools import wraps

import requests

from . import schema
from .utils import compact_mapping, to_iso8601
from .exceptions import NeonAPIError


__VERSION__ = "0.1.0"

NEON_API_KEY_ENVIRON = "NEON_API_KEY"
NEON_API_BASE_URL = "https://console.neon.tech/api/v2/"
ENABLE_PYDANTIC = True


def returns_model(model, is_array=False):
    """Decorator that returns a Pydantic dataclass.

    :param model: The Pydantic dataclass to return.
    :param is_array: Whether the return value is an array (default is False).
    :return: A Pydantic dataclass.

    If Pydantic is not enabled, the original return value is returned.
    """

    def decorator(func):
        @wraps(func)
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
    """Decorator that returns a subkey.

    :param key: The key to return.
    :return: The value of the key in the return value.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return getattr(func(*args, **kwargs), key)
            except AttributeError:
                return func(*args, **kwargs)[key]

        return wrapper

    return decorator


class NeonAPI:
    def __init__(self, api_key: str, *, base_url: str = None):
        """A Neon API client.

        :param api_key: The API key to use for authentication.
        :param base_url: The base URL of the Neon API (default is https://console.neon.tech/api/v2/).
        """

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

    def _request(
        self,
        method: str,
        path: str,
        **kwargs,
    ):
        """Send an HTTP request to the specified API path using the specified method.

        :param method: The HTTP method to use (e.g., "GET", "POST", "PUT", "DELETE").
        :param path: The API path to send the request to.
        :param kwargs: Additional keyword arguments to pass to the requests.Session.request method.
        :return: The JSON response from the server.
        """

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
            raise NeonAPIError(r.text)

        return r.json()

    def _url_join(self, *args):
        """Join a list of URL components into a single URL."""

        return "/".join(args)

    @classmethod
    def from_environ(cls):
        """Create a new Neon API client from the `NEON_API_KEY` environment variable."""

        return cls(os.environ[NEON_API_KEY_ENVIRON])

    @returns_model(schema.CurrentUserInfoResponse)
    def me(self) -> t.Dict[str, t.Any]:
        """Get the current user.

        More info: https://api-docs.neon.tech/reference/getcurrentuserinfo
        """

        return self._request("GET", "users/me")

    @returns_model(schema.ApiKeysListResponseItem, is_array=True)
    def api_keys(self) -> t.List[t.Dict[str, t.Any]]:
        """Get a list of API keys.

        :return: A dataclass representing the API key.

        More info: https://api-docs.neon.tech/reference/listapikeys
        """

        return self._request("GET", "api_keys")

    @returns_model(schema.ApiKeyCreateResponse)
    def api_key_create(self, **json: dict) -> t.Dict[str, t.Any]:
        """Create a new API key.

        :param json: The JSON paypload to send to the server.
        :return: A dataclass representing the API key.

        Example usage:

            >>> neon.api_key_create(name="My API Key")

        More info: https://api-docs.neon.tech/reference/createapikey
        """

        return self._request("POST", "api_keys", json=json)

    @returns_model(schema.ApiKeyRevokeResponse)
    def api_key_revoke(self, api_key_id: str) -> t.Dict[str, t.Any]:
        """Revoke an API key.

        :param api_key_id: The ID of the API key to revoke.
        :return: A dataclass representing the API key.

        More info: https://api-docs.neon.tech/reference/revokeapikey
        """
        return self._request("DELETE", f"api_keys/{ api_key_id }")

    @returns_model(schema.ProjectsResponse)
    def projects(
        self,
        *,
        shared: bool = False,
        cursor: str = None,
        limit: int = None,
    ) -> t.List[t.Dict[str, t.Any]]:
        """Get a list of projects. If shared is True, get a list of shared projects.

        :param shared: Whether to retrieve shared projects (default is False).
        :param cursor: The cursor for pagination (default is None).
        :param limit: The maximum number of projects to retrieve (default is None).
        :return: A list of dataclasses representing the projects.

        More info: https://api-docs.neon.tech/reference/listprojects
        """

        r_path = "projects" if not shared else "projects/shared"
        r_params = compact_mapping({"cursor": cursor, "limit": limit})

        return self._request("GET", r_path, params=r_params)

    @returns_model(schema.ProjectResponse)
    def project(self, project_id: str) -> t.Dict[str, t.Any]:
        """Get a project.

        :param project_id: The ID of the project.
        :return: A dataclass representing the project.

        More info: https://api-docs.neon.tech/reference/getproject
        """

        r_path = f"projects/{project_id}"

        return self._request("GET", r_path)

    @returns_model(schema.ConnectionUri)
    def connection_uri(self, project_id: str, database_name: str = None, role_name: str = None, pooled: bool = False) -> t.Dict[str, t.Any]:
        """Get a connection URI for a project.

        :param project_id: The ID of the project.
        :param database_name: The name of the database.
        :param role_name: The name of the role.
        :return: A dataclass representing the connection URI.

        More info: https://api-docs.neon.tech/reference/getconnectionuri
        """
        r_params = compact_mapping({"database_name": database_name, "role_name": role_name, "pooled": pooled})
        return self._request("GET", f"projects/{project_id}/connection_uri", params=r_params)

    @returns_model(schema.ProjectResponse)
    def project_create(self, **json: dict) -> t.Dict[str, t.Any]:
        """Create a new project. Accepts all keyword arguments for json body.

        :param json: The JSON paypload to send to the server.
        :return: A dataclass representing the project.

        More info: https://api-docs.neon.tech/reference/createproject
        """

        return self._request("POST", "projects", json=json)

    @returns_model(schema.ProjectResponse)
    def project_update(self, project_id: str, **json: dict) -> t.Dict[str, t.Any]:
        """Updates a project. Accepts all keyword arguments for json body.

        :param project_id: The ID of the project.
        :param json: The JSON paypload to send to the server.
        :return: A dataclass representing the project.

        More info: https://api-docs.neon.tech/reference/updateproject"""

        return self._request("PATCH", f"projects/{ project_id }", json=json)

    @returns_model(schema.ProjectResponse)
    def project_delete(self, project_id: str) -> t.Dict[str, t.Any]:
        """Delete a project.

        :param project_id: The ID of the project.
        :return: A dataclass representing the project.

        More info: https://api-docs.neon.tech/reference/deleteproject
        """

        return self._request("DELETE", f"projects/{ project_id }")

    @returns_model(schema.ProjectPermissions)
    def project_permissions(self, project_id: str) -> t.Dict[str, t.Any]:
        """Get a project permissions.

        :param project_id: The ID of the project.
        :return: A dataclass representing the project permissions.

        More info: https://api-docs.neon.tech/reference/listprojectpermissions
        """
        return self._request("GET", f"projects/{ project_id }/permissions")

    @returns_model(schema.ProjectPermission)
    def project_permissions_grant(
        self, project_id: str, **json: dict
    ) -> t.Dict[str, t.Any]:
        """Update a project permissions. Accepts all keyword arguments for json body.

        :param project_id: The ID of the project.
        :param json: The JSON paypload to send to the server.
        :return: A dataclass representing the project permissions.

        More info: https://api-docs.neon.tech/reference/grantpermissiontoproject
        """
        return self._request("POST", f"projects/{ project_id }/permissions", json=json)

    @returns_model(schema.ProjectPermission)
    def project_permissions_revoke(
        self, project_id: str, **json: dict
    ) -> t.Dict[str, t.Any]:
        """Update a project permissions. Accepts all keyword arguments for json body.

        :param project_id: The ID of the project.
        :param json: The JSON paypload to send to the server.
        :return: A dataclass representing the project permissions.

        More info: https://api-docs.neon.tech/reference/revokepermissionfromproject
        """
        return self._request(
            "DELETE", f"projects/{ project_id }/permissions", json=json
        )

    @returns_model(schema.BranchesResponse)
    def branches(
        self,
        project_id: str,
        *,
        cursor: str = None,
        limit: int = None,
    ) -> t.Dict[str, t.Any]:
        """Get a list of branches.

        :param project_id: The ID of the project.
        :param cursor: The cursor for pagination (default is None).
        :param limit: The maximum number of projects to retrieve (default is None).
        :return: A list of dataclasses representing the projects.

        More info: https://api-docs.neon.tech/reference/listprojectbranches
        """

        # Construct the request path and parameters.
        r_path = self._url_join("projects", project_id, "branches")
        r_params = compact_mapping({"cursor": cursor, "limit": limit})

        # Make the request.
        return self._request("GET", r_path, params=r_params)

    @returns_model(schema.BranchResponse)
    def branch(self, project_id: str, branch_id: str) -> t.Dict[str, t.Any]:
        """Get a branch.

        :param project_id: The ID of the project.
        :param branch_id: The ID of the branch.
        :return: A dataclass representing the branch.

        More info: https://api-docs.neon.tech/reference/getprojectbranch
        """

        # Construct the request path.
        r_path = self._url_join("projects", project_id, "branches", branch_id)

        # Make the request.
        return self._request("GET", r_path)

    @returns_model(schema.BranchOperations)
    def branch_create(self, project_id: str, **json: dict) -> t.Dict[str, t.Any]:
        """Create a new branch. Accepts all keyword arguments for json body.

        :param project_id: The ID of the project.
        :param json: The JSON paypload to send to the server.
        :return: A dataclass representing the branch.

        More info: https://api-docs.neon.tech/reference/createprojectbranch
        """
        return self._request("POST", f"projects/{ project_id }/branches", json=json)

    @returns_model(schema.BranchOperations)
    def branch_update(
        self, project_id: str, branch_id: str, **json: dict
    ) -> t.Dict[str, t.Any]:
        """Update a branch by branch_id. Accepts all keyword arguments for json body.

        :param project_id: The ID of the project.
        :param branch_id: The ID of the branch.
        :param json: The JSON paypload to send to the server.
        :return: A dataclass representing the branch.

        More info: https://api-docs.neon.tech/reference/updateprojectbranch
        """

        return self._request(
            "PATCH", f"projects/{ project_id }/branches/{ branch_id }", json=json
        )

    @returns_model(schema.BranchOperations)
    def branch_delete(self, project_id: str, branch_id: str) -> t.Dict[str, t.Any]:
        """Delete a branch by branch_id.

        :param project_id: The ID of the project.
        :param branch_id: The ID of the branch.
        :return: A dataclass representing the branch.

        More info: https://api-docs.neon.tech/reference/deleteprojectbranch
        """
        return self._request(
            "DELETE", f"projects/{ project_id }/branches/{ branch_id }"
        )

    @returns_model(schema.BranchOperations)
    def branch_set_as_primary(
        self, project_id: str, branch_id: str
    ) -> t.Dict[str, t.Any]:
        """Set a branch as primary by branch_id.

        :param project_id: The ID of the project.
        :param branch_id: The ID of the branch.
        :return: A dataclass representing the branch.

        More info: https://api-docs.neon.tech/reference/setprimaryprojectbranch"""

        return self._request(
            "POST", f"projects/{ project_id }/branches/{ branch_id }/set_as_primary"
        )

    @returns_model(schema.DatabasesResponse)
    def databases(
        self,
        project_id: str,
        branch_id: str,
        *,
        cursor: str = None,
        limit: int = None,
    ) -> t.List[t.Dict[str, t.Any]]:
        """Get a list of databases.

        :param project_id: The ID of the project.
        :param branch_id: The ID of the branch.
        :param cursor: The cursor for pagination (default is None).
        :param limit: The maximum number of projects to retrieve (default is None).
        :return: A list of dataclasses representing the database.

        More info: https://api-docs.neon.tech/reference/listprojectbranchdatabases
        """

        # Construct the request path and parameters.
        r_path = self._url_join(
            "projects", project_id, "branches", branch_id, "databases"
        )
        r_params = compact_mapping({"cursor": cursor, "limit": limit})

        # Make the request.
        return self._request("GET", r_path, params=r_params)

    @returns_model(schema.DatabaseResponse)
    def database(
        self, project_id: str, branch_id: str, database_id: str
    ) -> t.Dict[str, t.Any]:
        """Get a database.

        :param project_id: The ID of the project.
        :param branch_id: The ID of the branch.
        :param database_id: The ID of the database.
        :return: A dataclass representing the database.

        More info: https://api-docs.neon.tech/reference/getprojectbranchdatabase
        """

        # Construct the request path.
        r_path = self._url_join(
            "projects", project_id, "branches", branch_id, "databases", database_id
        )

        # Make the request.
        return self._request("GET", r_path)

    @returns_model(schema.DatabaseResponse)
    def database_create(
        self, project_id: str, branch_id: str, **json: dict
    ) -> t.Dict[str, t.Any]:
        """Create a new database. Accepts all keyword arguments for json body.

        :param project_id: The ID of the project.
        :param branch_id: The ID of the branch.
        :param json: The JSON paypload to send to the server.
        :return: A dataclass representing the database.

        More info: https://api-docs.neon.tech/reference/createprojectbranchdatabase
        """

        return self._request(
            "POST",
            f"projects/{ project_id }/branches/{ branch_id }/databases",
            json=json,
        )

    @returns_model(schema.DatabaseResponse)
    def database_update(
        self, project_id: str, branch_id: str, database_id: str, **json: dict
    ) -> t.Dict[str, t.Any]:
        """Update a database. Accepts all keyword arguments for json body.

        :param project_id: The ID of the project.
        :param branch_id: The ID of the branch.
        :param database_id: The ID of the database.
        :param json: The JSON paypload to send to the server.
        :return: A dataclass representing the database.

        More info: https://api-docs.neon.tech/reference/updateprojectbranchdatabase
        """

        return self._request(
            "PUT",
            f"projects/{ project_id }/branches/{ branch_id }/databases/{ database_id }",
            json=json,
        )

    @returns_model(schema.DatabaseResponse)
    def database_delete(
        self, project_id: str, branch_id: str, database_id: str
    ) -> t.Dict[str, t.Any]:
        """Delete a database by database_id.

        :param project_id: The ID of the project.
        :param branch_id: The ID of the branch.
        :param database_id: The ID of the database.
        :return: A dataclass representing the database.

        More info: https://api-docs.neon.tech/reference/deleteprojectbranchdatabase
        """

        return self._request(
            "DELETE",
            f"projects/{ project_id }/branches/{ branch_id }/databases/{ database_id }",
        )

    @returns_model(schema.EndpointsResponse)
    def endpoints(self, project_id: str) -> t.Dict[str, t.Any]:
        """Get a list of endpoints for a given branch

        :param project_id: The ID of the project.
        :return: A list of dataclasses representing the endpoints.

        More info: https://api-docs.neon.tech/reference/listprojectendpoints
        """
        return self._request("GET", f"projects/{ project_id }/endpoints")

    @returns_model(schema.EndpointResponse)
    def endpoint(self, project_id: str, endpoint_id: str) -> t.Dict[str, t.Any]:
        """Get an endpoint for a given branch.

        :param project_id: The ID of the project.
        :param endpoint_id: The ID of the endpoint.
        :return: A dataclass representing the endpoint.

        More info: https://api-docs.neon.tech/reference/getprojectendpoint
        """
        return self._request(
            "GET",
            f"projects/{ project_id }/endpoints/{ endpoint_id }",
        )

    @returns_model(schema.EndpointOperations)
    def endpoint_create(
        self,
        project_id: str,
        **json: dict,
    ) -> t.Dict[str, t.Any]:
        """Create a new endpoint. Accepts all keyword arguments for json body.

        :param project_id: The ID of the project.
        :param json: The JSON paypload to send to the server.
        :return: A dataclass representing the endpoint.

        More info: https://api-docs.neon.tech/reference/createprojectendpoint
        """

        return self._request("POST", f"projects/{ project_id }/endpoints", json=json)

    @returns_model(schema.EndpointOperations)
    def endpoint_delete(self, project_id: str, endpoint_id: str) -> t.Dict[str, t.Any]:
        """Delete an endpoint by endpoint_id.

        :param project_id: The ID of the project.
        :param endpoint_id: The ID of the endpoint.
        :return: A dataclass representing the endpoint.

        More info: https://api-docs.neon.tech/reference/deleteprojectendpoint
        """

        return self._request(
            "DELETE",
            f"projects/{ project_id }/endpoints/{ endpoint_id }",
        )

    @returns_model(schema.EndpointOperations)
    def endpoint_update(
        self, project_id: str, endpoint_id: str, **json: dict
    ) -> t.Dict[str, t.Any]:
        """Update an endpoint. Accepts all keyword arguments for json body.

        :param project_id: The ID of the project.
        :param endpoint_id: The ID of the endpoint.
        :param json: The JSON paypload to send to the server.
        :return: A dataclass representing the endpoint.

        More info: https://api-docs.neon.tech/reference/updateprojectendpoint
        """

        return self._request(
            "PATCH",
            f"projects/{ project_id }/endpoints/{ endpoint_id }",
            json=json,
        )

    @returns_model(schema.EndpointOperations)
    def endpoint_start(self, project_id: str, endpoint_id: str):
        """Start an endpoint by endpoint_id.

        :param project_id: The ID of the project.
        :param endpoint_id: The ID of the endpoint.
        :return: A dataclass representing the endpoint.

        More info: https://api-docs.neon.tech/reference/startprojectendpoint"""

        return self._request(
            "POST",
            f"projects/{ project_id }/endpoints/{ endpoint_id }/start",
        )

    @returns_model(schema.EndpointOperations)
    def endpoint_suspend(self, project_id: str, endpoint_id: str):
        """Suspend an endpoint by endpoint_id.

        :param project_id: The ID of the project.
        :param endpoint_id: The ID of the endpoint.
        :return: A dataclass representing the endpoint.

        More info: https://api-docs.neon.tech/reference/suspendprojectendpoint
        """

        return self._request(
            "POST",
            f"projects/{ project_id }/endpoints/{ endpoint_id }/suspend",
        )

    @returns_model(schema.RolesResponse)
    def roles(self, project_id: str, branch_id: str) -> t.Dict[str, t.Any]:
        """Get a list of roles for a given branch.

        :param project_id: The ID of the project.
        :param branch_id: The ID of the branch.
        :return: A list of dataclasses representing the roles.

        More info: https://api-docs.neon.tech/reference/listprojectbranchroles
        """

        return self._request(
            "GET", f"projects/{ project_id }/branches/{ branch_id }/roles"
        )

    @returns_model(schema.RoleResponse)
    def role(
        self, project_id: str, branch_id: str, role_name: str
    ) -> t.Dict[str, t.Any]:
        """Get a role for a given branch.

        :param project_id: The ID of the project.
        :param branch_id: The ID of the branch.
        :param role_name: The name of the role.
        :return: A dataclass representing the role.

        More info: https://api-docs.neon.tech/reference/getprojectbranchrole

        """
        return self._request(
            "GET", f"projects/{ project_id }/branches/{ branch_id }/roles/{ role_name }"
        )

    @returns_model(schema.RoleOperations)
    def role_create(
        self,
        project_id: str,
        branch_id: str,
        role_name: str,
    ) -> t.Dict[str, t.Any]:
        """Create a new role. Accepts all keyword arguments for json body.

        :param project_id: The ID of the project.
        :param branch_id: The ID of the branch.
        :param role_name: The name of the role.
        :return: A dataclass representing the role.

        More info: https://api-docs.neon.tech/reference/createprojectbranchrole
        """

        return self._request(
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
        """Delete a role by given role name.

        :param project_id: The ID of the project.
        :param branch_id: The ID of the branch.
        :param role_name: The name of the role.
        :return: A dataclass representing the role.

        More info: https://api-docs.neon.tech/reference/deleteprojectbranchrole
        """

        return self._request(
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
        """Get a role password.

        :param project_id: The ID of the project.
        :param branch_id: The ID of the branch.
        :param role_name: The name of the role.
        :return: A dataclass representing the role password.

        More info: https://api-docs.neon.tech/reference/getprojectbranchrolepassword"""

        return self._request(
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
        """Reset a role password.

        :param project_id: The ID of the project.
        :param branch_id: The ID of the branch.
        :param role_name: The name of the role.
        :return: A dataclass representing the role.

        More info: https://api-docs.neon.tech/reference/resetprojectbranchrolepassword
        """

        return self._request(
            "POST",
            f"projects/{ project_id }/branches/{ branch_id }/roles/{ role_name }/reset_password",
        )

    @returns_model(schema.OperationsResponse)
    def operations(
        self,
        project_id: str,
        *,
        cursor: str = None,
        limit: int = None,
    ) -> t.Dict[str, t.Any]:
        """Get a list of operations.

        :param project_id: The ID of the project.
        :param cursor: The cursor for pagination (default is None).
        :param limit: The maximum number of projects to retrieve (default is None).
        :return: A list of dataclasses representing the operations.

        More info: https://api-docs.neon.tech/reference/listprojectoperations
        """

        r_params = compact_mapping({"cursor": cursor, "limit": limit})
        return self._request(
            "GET", f"projects/{ project_id }/operations", params=r_params
        )

    @returns_model(schema.OperationResponse)
    def operation(self, project_id: str, operation_id: str) -> t.Dict[str, t.Any]:
        """Get an operation.

        :param project_id: The ID of the project.
        :param operation_id: The ID of the operation.
        :return: A dataclass representing the operation.

        More info: https://api-docs.neon.tech/reference/getprojectoperation
        """

        return self._request(
            "GET", f"projects/{ project_id }/operations/{ operation_id }"
        )

    @returns_model(schema.ProjectsConsumptionResponse)
    def consumption(
        self,
        *,
        cursor: str = None,
        limit: int = None,
        from_date: datetime = None,
        to_date: datetime = None,
    ) -> t.Dict[str, t.Any]:
        """Experimental — get a list of consumption metrics for all projects.

        :param cursor: The cursor for pagination (default is None).
        :param limit: The maximum number of projects to retrieve (default is None).
        :param from_date: The start date for the consumption metrics (default is None).
        :param to_date: The end date for the consumption metrics (default is None).
        :return: A dataclass representing the consumption metrics.

        More info: https://api-docs.neon.tech/reference/listprojectsconsumption
        """

        # Convert datetime objects to ISO 8601 strings.
        from_date = (
            to_iso8601(from_date) if isinstance(from_date, datetime) else from_date
        )
        to_date = to_iso8601(to_date) if isinstance(to_date, datetime) else to_date

        # Construct the request parameters.
        r_params = compact_mapping(
            {"cursor": cursor, "limit": limit, "from": from_date, "to": to_date}
        )

        # Make the request.
        return self._request("GET", "consumption/projects", params=r_params)
