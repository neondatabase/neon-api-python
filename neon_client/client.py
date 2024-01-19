import os
import typing as t

import requests

from .utils import compact_mapping
from .exceptions import NeonClientException


__VERSION__ = "0.1.0"

NEON_API_KEY_ENVIRON = "NEON_API_KEY"
NEON_API_BASE_URL = "https://console.neon.tech/api/v2/"


class NeonAPI:
    def __init__(self, api_key: str, *, base_url: str = None):
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
        """Create a new Neon API client from the NEON_API_KEY environment variable."""

        return cls(os.environ[NEON_API_KEY_ENVIRON])

    def me(self) -> t.Dict[str, t.Any]:
        """Get the current user."""
        return self.request("GET", "users/me")

    def api_keys(self) -> t.List[t.Dict[str, t.Any]]:
        """Get a list of API keys."""
        return self.request("GET", "api_keys")

    def api_key_create(self, key_name: str):
        """Create a new API key."""
        return self.request("POST", "api_keys", json={"name": key_name})

    def api_key_revoke(self, api_key_id: str) -> t.Dict[str, t.Any]:
        """Revoke an API key."""
        return self.request("DELETE", f"api_keys/{ api_key_id }")

    def projects(
        self,
        *,
        shared: bool = False,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> t.List[t.Dict[str, t.Any]]:
        """Get a list of projects."""

        r_path = "projects" if not shared else "projects/shared"
        r_params = compact_mapping({"cursor": cursor, "limit": limit})

        return self.request("GET", r_path, params=r_params)

    def project(self, project_id: str) -> t.Dict[str, t.Any]:
        """Get a project."""

        r_path = self.url_join("projects", project_id)

        return self.request(
            "GET",
            r_path,
        )

    def project_create(self, **json: dict) -> t.Dict[str, t.Any]:
        """Create a new project. Accepts all keyword arguments for json body."""

        return self.request("POST", "projects", json=json)

    def project_delete(self, project_id: str) -> t.Dict[str, t.Any]:
        """Delete a project."""

        return self.request("DELETE", f"projects/{ project_id }")

    def branches(
        self,
        project_id: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ):
        """Get a list of branches."""

        # Construct the request path and parameters.
        r_path = self.url_join("projects", project_id, "branches")
        r_params = compact_mapping({"cursor": cursor, "limit": limit})

        # Make the request.
        return self.request("GET", r_path, params=r_params)

    def branch(self, project_id: str, branch_id: str) -> t.Dict[str, t.Any]:
        """Get a branch."""

        # Construct the request path.
        r_path = self.url_join("projects", project_id, "branches", branch_id)

        # Make the request.
        return self.request("GET", r_path)

    def branch_create(self, project_id: str, **json: dict) -> t.Dict[str, t.Any]:
        """Create a new branch. Accepts all keyword arguments for json body."""

        return self.request("POST", f"projects/{ project_id }/branches", json=json)

    def branch_delete(self, project_id: str, branch_id: str) -> t.Dict[str, t.Any]:
        """Delete a branch."""

        return self.request("DELETE", f"projects/{ project_id }/branches/{ branch_id }")

    def databases(
        self,
        project_id: str,
        branch_id: str,
        *,
        cursor: str | None = None,
        limit: int | None = None,
    ) -> t.List[t.Dict[str, t.Any]]:
        """Get a list of databases."""

        # Construct the request path and parameters.
        r_path = self.url_join(
            "projects", project_id, "branches", branch_id, "databases"
        )
        r_params = compact_mapping({"cursor": cursor, "limit": limit})

        # Make the request.
        return self.request("GET", r_path, params=r_params)

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

    def database_create(
        self, project_id: str, branch_id: str, **json: dict
    ) -> t.Dict[str, t.Any]:
        """Create a new database. Accepts all keyword arguments for json body."""

        return self.request(
            "POST",
            f"projects/{ project_id }/branches/{ branch_id }/databases",
            json=json,
        )

    def database_update(
        self, project_id: str, branch_id: str, database_id: str, **json: dict
    ) -> t.Dict[str, t.Any]:
        """Update a database. Accepts all keyword arguments for json body."""

        return self.request(
            "PUT",
            f"projects/{ project_id }/branches/{ branch_id }/databases/{ database_id }",
            json=json,
        )

    def database_delete(
        self, project_id: str, branch_id: str, database_id: str
    ) -> t.Dict[str, t.Any]:
        """Delete a database."""

        return self.request(
            "DELETE",
            f"projects/{ project_id }/branches/{ branch_id }/databases/{ database_id }",
        )

    def operations(self, project_id: str) -> t.List[t.Dict[str, t.Any]]:
        """Get a list of operations."""
        return self.request("GET", f"projects/{ project_id }/operations")

    def operation(self, project_id: str, operation_id: str) -> t.Dict[str, t.Any]:
        """Get an operation."""
        return self.request(
            "GET", f"projects/{ project_id }/operations/{ operation_id }"
        )
