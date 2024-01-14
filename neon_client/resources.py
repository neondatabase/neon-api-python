from typing import List

from .http_client import Neon_API_V2
from .openapi_models import (
    ApiKeyCreateRequest,
    ApiKeyCreateResponse,
    ApiKeyRevokeResponse,
    ApiKeysListResponseItem,
    CurrentUserInfoResponse,
    Project,
    ProjectResponse,
    ProjectUpdateRequest,
    ProjectsResponse,
    DatabaseResponse,
    DatabasesResponse,
    DatabaseUpdateRequest,
    Database,
    Database1,
    Database2,
    DatabaseCreateRequest,
    BranchesResponse,
    BranchResponse,
)
from .utils import validate_obj_model


class Resource:
    base_path = None

    def __init__(self, api: Neon_API_V2):
        self.api = api


class UserResource(Resource):
    """A resource for interacting with users."""

    base_path = "users"
    response_model = CurrentUserInfoResponse

    def get_current_user_info(self):
        """Get information about the user."""

        return self.api.request(
            method="GET",
            path=self.api.url_join(self.path, "me"),
            response_model=self.response_model,
        )


class APIKeyResource(Resource):
    """A resource for interacting with API keys."""

    path = "api_keys"
    response_model = ApiKeysListResponseItem
    # response_model_single =

    def get_list(self):
        """Get a list of API keys."""

        return self.api.request(
            method="GET",
            path=self.path,
            response_model=self.response_model,
            response_is_array=True,
        )

    def create(self, key_name: str):
        """Create a new API key."""

        return self.api.request(
            method="POST",
            path=self.path,
            json=ApiKeyCreateRequest(key_name=key_name).model_dump(),
            response_model=ApiKeyCreateResponse,
        )

    def revoke(self, key_id: str):
        """Revoke an API key."""

        return self.api.request(
            method="DELETE",
            path=self.api.url_join(self.path, key_id),
            response_model=ApiKeyRevokeResponse,
        )

    def get(self, key_id: str):
        """Get an API key."""

        return self.api.request(
            "GET",
            f"api_keys/{key_id}",
            response_model=ApiKeyRevokeResponse,
        )


class ProjectResource(Resource):
    """A resource for interacting with projects."""

    path = "projects"
    response_model = ProjectsResponse
    response_model_single = ProjectResponse

    def get_list(self, *, shared=False):
        """Get a list of projects."""

        project_response = self.api.request(
            method="GET",
            path=(self.api.url_join(self.path, "shared") if shared else self.path),
            response_model=self.response_model,
        )
        return project_response.projects

    def get(self, project_id: str):
        """Get a project."""

        project_response = self.api.request(
            method="GET",
            path=self.api.url_join(self.path, project_id),
            response_model=self.response_model_single,
        )
        return project_response.project

    def create(self, name: str, **kwargs):
        """Create a new project."""

        project_create_response = self.api.request(
            method="POST",
            path=self.path,
            json={"project": {"name": name, **kwargs}},
            response_model=self.response_model_single,
        )
        return project_create_response.project

    def update(self, project: Project):
        """Update a project."""

        payload = ProjectUpdateRequest(project=project.model_dump())

        return self.api.request(
            method="PATCH",
            path=self.api.url_join(self.path, project.id),
            json={"project": payload.model_dump()},
            response_model=self.response_model_single,
        )

    def delete(self, project_id: str):
        """Delete a project."""

        return self.api.request(
            method="DELETE",
            path=self.api.url_join(self.path, project_id),
            response_model=self.response_model_single,
        )


class DatabaseResource(Resource):
    path = "databases"
    response_model = DatabasesResponse
    response_model_single = DatabaseResponse

    CreateRequest = DatabaseCreateRequest
    UpdateRequest = DatabaseUpdateRequest
    Database = Database

    def _extract_database(self, obj):
        """Extract a database from the specified object."""

        assert isinstance(obj, (DatabaseCreateRequest, Database1, Database2, Database))

        # Object mappings.
        if isinstance(obj, DatabaseCreateRequest):
            obj = obj.database.model_dump()
        if isinstance(obj, Database1):
            obj = obj.database.model_dump()
        if isinstance(obj, Database2):
            obj = obj.database.model_dump()
        if isinstance(obj, Database):
            obj = obj.model_dump()

        return obj

    def get_list(self, project_id: str, branch_id: str):
        """Get a list of databases.

        See also: https://api-docs.neon.tech/reference/listprojectbranchdatabases
        """

        databases_response = self.api.request(
            method="GET",
            path=self.api.url_join(
                "projects", project_id, "branches", branch_id, "databases"
            ),
            response_model=DatabasesResponse,
        )

        return databases_response.databases

    def get(
        self,
        project_id: str,
        branch_id: str,
        database_name: str,
    ):
        """Get a database."""

        database_response = self.api.request(
            method="GET",
            path=self.api.url_join(
                "projects",
                project_id,
                "branches",
                branch_id,
                "databases",
                database_name,
            ),
            response_model=DatabaseResponse,
        )
        return database_response.database

    def create(
        self,
        project_id: str,
        branch_id: str,
        db: DatabaseCreateRequest | Database1 | Database2 | Database,
    ):
        """Create a new database."""

        db = self._extract_database(db)

        database_create_response = self.api.request(
            method="POST",
            path=self.api.url_join(
                "projects", project_id, "branches", branch_id, "databases"
            ),
            json=DatabaseCreateRequest(database=db).model_dump(),
            response_model=DatabaseResponse,
        )
        return database_create_response.database

    def update(
        self,
        project_id: str,
        branch_id: str,
        database_id: str,
        db: DatabaseUpdateRequest | Database2,
    ):
        """Update a database."""

        db = self._extract_database(db)

        database_update_response = self.api.request(
            method="PATCH",
            path=self.api.url_join(
                "projects", project_id, "branches", branch_id, "databases", database_id
            ),
            json=DatabaseUpdateRequest(database=db).model_dump(),
            response_model=DatabaseResponse,
        )
        return database_update_response.database


class BranchResource(Resource):
    """A resource for interacting with branches."""

    path = "branches"
    response_model = BranchesResponse
    response_model_single = BranchResponse

    def get_list(self, project_id: str):
        """Get a list of branches."""

        branches_response = self.api.request(
            method="GET",
            path=self.api.url_join("projects", project_id, "branches"),
            response_model=self.response_model,
        )
        return branches_response.branches

    def get(self, project_id: str, branch_id: str):
        """Get a branch."""

        branch_response = self.api.request(
            method="GET",
            path=self.api.url_join("projects", project_id, "branches", branch_id),
            response_model=self.response_model_single,
        )

        return branch_response.branch


class ResourceCollection:
    """A collection of resources."""

    def __init__(self, api: Neon_API_V2):
        # Initialize resources.
        self.api_keys = APIKeyResource(api)
        self.users = UserResource(api)
        self.projects = ProjectResource(api)
        self.databases = DatabaseResource(api)
        self.branches = BranchResource(api)
