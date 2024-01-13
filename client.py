from typing import List
import requests

from model import *


class NeonAPI:
    def __init__(
        self, api_key: str, *, base_url: str = "https://console.neon.tech/api/v2/"
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()

    def _request(self, method: str, path: str, **kwargs):
        # Set HTTP headers for outgoing requests.
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.api_key}"
        headers["Accept"] = "application/json"
        headers["Content-Type"] = "application/json"

        return self.session.request(
            method, self.base_url + path, headers=headers, **kwargs
        )


class NeonClient(NeonAPI):
    def __init__(self, api_key: str, **kwargs):
        super().__init__(api_key, **kwargs)
        # self.api_keys = APIKeyResource(self)

    def me(self) -> CurrentUserInfoResponse:
        """Get information about the user."""

        r = self._request("GET", "users/me")
        r.raise_for_status()

        return CurrentUserInfoResponse(**r.json())

    def get_api_keys(self) -> List[ApiKeysListResponseItem]:
        """Get a list of API keys."""

        r = self._request("GET", "api_keys")
        r.raise_for_status()

        return [ApiKeysListResponseItem(**item) for item in r.json()]

    def create_api_key(self, name: str) -> ApiKeyCreateResponse:
        """Create a new API key."""

        r = self._request("POST", "api_keys", json={"key_name": name})
        r.raise_for_status()

        return ApiKeyCreateResponse(**r.json())

    def delete_api_key(self, key_id: str) -> ApiKeyRevokeResponse:
        """Delete an API key."""

        r = self._request("DELETE", f"api_keys/{key_id}")
        r.raise_for_status()

        return ApiKeyRevokeResponse(**r.json())

    def get_projects(self) -> List[ProjectListItem]:
        """Get a list of projects."""

        r = self._request("GET", "projects")
        r.raise_for_status()

        return [ProjectListItem(**item) for item in r.json()["projects"]]

    def create_project(self, project_id: str) -> ProjectCreateRequest:
        """Create a new project."""

        r = self._request("POST", "projects", json={"project": {"name": project_id}})
        r.raise_for_status()

        return ProjectCreateRequest(**r.json())

    def delete_project(self, project_id: str) -> ProjectUpdateRequest:
        """Delete a project."""

        r = self._request("DELETE", f"projects/{project_id}")
        r.raise_for_status()

        return ProjectUpdateRequest(**r.json())
