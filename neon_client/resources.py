from typing import List

from .http_client import Neon_API_V2
from .openapi_models import (
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
)
from .utils import validate_with_model


class Resource:
    base_path = None

    def __init__(self, api: Neon_API_V2):
        self.api = api


class UserResource(Resource):
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
    path = "api_keys"
    response_model = ApiKeysListResponseItem

    def get_keys(self):
        """Get a list of API keys."""

        keys = self.api.request(
            method="GET",
            path=self.path,
            response_model=self.response_model,
            response_is_array=True,
        )

    def create_key(self, name: str):
        """Create a new API key."""

        return self.api.request(
            method="POST",
            path=self.path,
            json={"key_name": name},
            response_model=ApiKeyCreateResponse,
        )

    def revoke_key(self, key_id: str):
        """Revoke an API key."""

        return self.api.request(
            method="DELETE",
            path=self.api.url_join(self.path, key_id),
            response_model=ApiKeyRevokeResponse,
        )

    def get_key(self, key_id: str):
        """Get an API key."""

        return self.api.request(
            "GET",
            f"api_keys/{key_id}",
            response_model=ApiKeyRevokeResponse,
        )


class ProjectResource(Resource):
    path = "projects"
    response_model = ProjectsResponse
    response_model_single = ProjectResponse

    def get_projects(self, *, shared=False):
        """Get a list of projects."""

        project_response = self.api.request(
            method="GET",
            path=(self.api.url_join(self.path, "shared") if shared else self.path),
            response_model=self.response_model,
        )
        return project_response.projects

    def get_project(self, project_id: str):
        """Get a project."""

        project_response = self.api.request(
            method="GET",
            path=self.api.url_join(self.path, project_id),
            response_model=self.response_model_single,
        )
        return project_response.project

    def create_project(self, name: str, **kwargs):
        """Create a new project."""

        project_create_response = self.api.request(
            method="POST",
            path=self.path,
            json={"project": {"name": name, **kwargs}},
            response_model=self.response_model_single,
        )
        return project_create_response.project

    def update_project(self, project: Project):
        """Update a project."""

        payload = ProjectUpdateRequest(project=project.model_dump())

        return self.api.request(
            method="PATCH",
            path=self.api.url_join(self.path, project.id),
            json={"project": payload.model_dump()},
            response_model=self.response_model_single,
        )

    # def new(self, project_id: str):
    #     """Create a new project."""

    #     project_create_response = self.api.request(
    #         method="POST",
    #         path=self.path,
    #         json={"project": {"name": project_id}},
    #         response_model=self.response_model,
    #     )
    #     return project_create_response.project

    # def get_project(self, project_id: str) -> ProjectResponse:
    #     """Get a project."""

    #     return self.api.request(
    #         "GET", f"projects/{project_id}", response_model=ProjectResponse
    #     )

    # def update_project(self, project: Project) -> ProjectResponse:
    #     """Update a project."""

    #     payload = ProjectUpdateRequest(project=project.model_dump())

    #     return self.api.request(
    #         "PATCH",
    #         f"projects/{project.id}",
    #         json={"project": payload.model_dump()},
    #         response_model=ProjectResponse,
    #     )

    # def delete_project(self, project_id: str) -> ProjectResponse:
    #     """Delete a project."""

    #     return self.api.request(
    #         "DELETE", f"projects/{project_id}", response_model=ProjectResponse
    #     )


class DatabaseResource(Resource):
    def get_databases(self, project_id: str, branch_id: str):
        """Get a list of databases."""

        databases_response = self.api.request(
            method="GET",
            path=self.api.url_join(
                "projects", project_id, "branches", branch_id, "databases"
            ),
            response_model=DatabasesResponse,
        )

        return databases_response.databases

    def get_database(self, project_id: str, database_id: str):
        """Get a database."""

        database_response = self.api.request(
            method="GET",
            path=self.api.url_join("projects", project_id, "databases", database_id),
            response_model=DatabaseResponse,
        )
        return database_response.database

    @validate_with_model(DatabaseCreateRequest)
    def create_database(
        self, project_id: str, branch_id: str, *, obj: DatabaseCreateRequest, **kwargs
    ):
        """Create a new database."""
        # TODO: untested.

        database_create_response = self.api.request(
            method="POST",
            path=self.api.url_join(
                "projects", project_id, "branches", branch_id, "databases"
            ),
            json=obj.model_dump(),
            response_model=DatabaseResponse,
        )
        return database_create_response.database

    def update_database(self, project_id: str, database: Database2):
        """Update a database."""
        # TODO: This is not working yet.

        payload = DatabaseUpdateRequest(database=database.model_dump())

        return self.api.request(
            method="PATCH",
            path=self.api.url_join("projects", project_id, "databases", database.id),
            json=payload.model_dump(),
            response_model=DatabaseResponse,
        )

    def new(self, name, **kwargs):
        """Create a new database."""

        db = Database1.model_construct(name=name, **kwargs)
        return db
