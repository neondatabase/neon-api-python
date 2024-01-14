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
    OperationResponse,
    OperationsResponse,
    PaginationResponse,
)
from .utils import validate_obj_model


class PagedOperationsResponse(OperationsResponse, PaginationResponse):
    """A response containing a list of operations and pagination information."""

    pass


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

    base_path = "api_keys"

    def get_list(self):
        """Get a list of API keys."""

        return self.api.request(
            method="GET",
            path=self.base_path,
            response_model=ApiKeysListResponseItem,
            response_is_array=True,
        )

    def create(self, key_name: str):
        """Create a new API key."""

        return self.api.request(
            method="POST",
            path=self.base_path,
            json=ApiKeyCreateRequest(key_name=key_name).model_dump(),
            response_model=ApiKeyCreateResponse,
        )

    def revoke(self, key_id: str):
        """Revoke an API key."""

        return self.api.request(
            method="DELETE",
            path=self.api.url_join(self.base_path, str(key_id)),
            response_model=ApiKeyRevokeResponse,
        )


class ProjectResource(Resource):
    """A resource for interacting with projects."""

    base_path = "projects"
    response_model = ProjectsResponse
    response_model_single = ProjectResponse

    def get_list(self, *, shared=False):
        """Get a list of projects."""

        project_response = self.api.request(
            method="GET",
            path=(
                self.api.url_join(self.base_path, "shared")
                if shared
                else self.base_path
            ),
            response_model=self.response_model,
        )
        return project_response.projects

    def get(self, project_id: str):
        """Get a project."""

        project_response = self.api.request(
            method="GET",
            path=self.api.url_join(self.base_path, project_id),
            response_model=self.response_model_single,
        )
        return project_response.project

    def create(self, name: str, **kwargs):
        """Create a new project."""

        project_create_response = self.api.request(
            method="POST",
            path=self.base_path,
            json={"project": {"name": name, **kwargs}},
            response_model=self.response_model_single,
        )
        return project_create_response.project

    def update(self, project: Project):
        """Update a project."""

        payload = ProjectUpdateRequest(project=project.model_dump())

        return self.api.request(
            method="PATCH",
            path=self.api.url_join(self.base_path, project.id),
            json={"project": payload.model_dump()},
            response_model=self.response_model_single,
        )

    def delete(self, project_id: str):
        """Delete a project."""

        return self.api.request(
            method="DELETE",
            path=self.api.url_join(self.base_path, project_id),
            response_model=self.response_model_single,
        )


class DatabaseResource(Resource):
    base_path = "databases"
    response_model = DatabasesResponse
    response_model_single = DatabaseResponse

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

        return self.api.request(
            method="GET",
            path=self.api.url_join(
                "projects", project_id, "branches", branch_id, "databases"
            ),
            response_model=DatabasesResponse,
        ).model_dump()

    def get(
        self,
        project_id: str,
        branch_id: str,
        database_name: str,
    ):
        """Get a database."""

        return self.api.request(
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
        ).model_dump()

    def create(
        self,
        project_id: str,
        branch_id: str,
        db: DatabaseCreateRequest | Database1 | Database2 | Database,
    ):
        """Create a new database."""

        db = self._extract_database(db)

        return self.api.request(
            method="POST",
            path=self.api.url_join(
                "projects", project_id, "branches", branch_id, "databases"
            ),
            json=DatabaseCreateRequest(database=db).model_dump(),
            response_model=DatabaseResponse,
        ).model_dump()

    def update(
        self,
        project_id: str,
        branch_id: str,
        database_id: str,
        db: DatabaseUpdateRequest | Database2,
    ):
        """Update a database."""

        db = self._extract_database(db)

        return self.api.request(
            method="PATCH",
            path=self.api.url_join(
                "projects", project_id, "branches", branch_id, "databases", database_id
            ),
            json=DatabaseUpdateRequest(database=db).model_dump(),
            response_model=DatabaseResponse,
        ).model_dump()


class BranchResource(Resource):
    """A resource for interacting with branches."""

    path = "branches"
    response_model = BranchesResponse
    response_model_single = BranchResponse

    def get_list(self, project_id: str):
        """Get a list of branches."""

        return self.api.request(
            method="GET",
            path=self.api.url_join("projects", project_id, "branches"),
            response_model=self.response_model,
        ).model_dump()

    def get(self, project_id: str, branch_id: str):
        """Get a branch."""

        return self.api.request(
            method="GET",
            path=self.api.url_join("projects", project_id, "branches", branch_id),
            response_model=self.response_model_single,
        ).model_dump()


class OperationResource(Resource):
    """A resource for interacting with operations."""

    base_path = "operations"

    def get_list(
        self,
        project_id: str,
        cursor: int | None = None,
        limit: int | None = None,
    ):
        """Get a list of operations."""

        operations_params = {}
        if cursor is not None:
            operations_params["cursor"] = cursor
        if limit is not None:
            operations_params["limit"] = limit

        return self.api.request(
            method="GET",
            path=self.api.url_join("projects", project_id, "operations"),
            params=operations_params,
            response_model=PagedOperationsResponse,
        ).model_dump()

    def get(self, project_id: str, operation_id: str):
        """Get an operation."""

        return self.api.request(
            method="GET",
            path=self.api.url_join("projects", project_id, "operations", operation_id),
            response_model=OperationResponse,
        ).model_dump()


class ResourceCollection:
    """A collection of resources."""

    def __init__(self, api: Neon_API_V2):
        # Initialize resources.
        self.api_keys = APIKeyResource(api)
        self.users = UserResource(api)
        self.projects = ProjectResource(api)
        self.databases = DatabaseResource(api)
        self.branches = BranchResource(api)
        self.operations = OperationResource(api)
