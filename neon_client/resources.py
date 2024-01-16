from typing import List
from fastapi.encoders import jsonable_encoder

from .http_client import Neon_API_V2
from . import models
from .utils import validate_obj_model


class PagedOperationsResponse(models.OperationsResponse, models.PaginationResponse):
    """A response containing a list of operations and pagination information."""

    pass


class PagedProjectsResponse(models.ProjectsResponse, models.PaginationResponse):
    """A response containing a list of projects and pagination information."""

    pass


class Resource:
    base_path = None

    def __init__(self, api: Neon_API_V2):
        self.api = api


class UserResource(Resource):
    """A resource for interacting with users."""

    base_path = "users"

    def get_current_user_info(self):
        """Get information about the user."""

        return self.api.request(
            method="GET",
            path=self.api.url_join(self.base_path, "me"),
            response_model=models.CurrentUserInfoResponse,
        )


class APIKeyResource(Resource):
    """A resource for interacting with API keys."""

    base_path = "api_keys"

    def get_list(self):
        """Get a list of API keys."""

        return self.api.request(
            method="GET",
            path=self.base_path,
            response_model=models.ApiKeysListResponseItem,
            response_is_array=True,
        )

    def create(self, key_name: str):
        """Create a new API key."""

        return self.api.request(
            method="POST",
            path=self.base_path,
            json=models.ApiKeyCreateRequest(key_name=key_name).model_dump(),
            response_model=models.ApiKeyCreateResponse,
        )

    def revoke(self, key_id: str):
        """Revoke an API key."""

        return self.api.request(
            method="DELETE",
            path=self.api.url_join(self.base_path, str(key_id)),
            response_model=models.ApiKeyRevokeResponse,
        )


class ProjectResource(Resource):
    """A resource for interacting with projects."""

    base_path = "projects"

    def get_list(
        self,
        *,
        cursor: int | None = None,
        limit: int | None = None,
        shared: bool = False
    ):
        """Get a list of projects."""

        project_params = {}
        if cursor is not None:
            project_params["cursor"] = cursor
        if limit is not None:
            project_params["limit"] = limit

        return self.api.request(
            method="GET",
            path=(
                self.api.url_join(self.base_path, "shared")
                if shared
                else self.base_path
            ),
            params=project_params,
            response_model=PagedProjectsResponse,
        )

    def get(self, project_id: str):
        """Get a project."""

        return self.api.request(
            method="GET",
            path=self.api.url_join(self.base_path, project_id),
            response_model=models.ProjectResponse,
        )

    def create(self, **kwargs):
        """Create a new project."""

        return self.api.request(
            method="POST",
            path=self.base_path,
            json={"project": kwargs},
            response_model=models.ProjectResponse,
        ).model_dump()

    def update(self, project: models.Project):
        """Update a project."""

        payload = models.ProjectUpdateRequest(project=project.model_dump())

        return self.api.request(
            method="PATCH",
            path=self.api.url_join(self.base_path, project.id),
            json={"project": payload.model_dump()},
            response_model=models.ProjectResponse,
        )

    def delete(self, project_id: str):
        """Delete a project."""

        return self.api.request(
            method="DELETE",
            path=self.api.url_join(self.base_path, project_id),
            response_model=models.ProjectResponse,
        )


class DatabaseResource(Resource):
    base_path = "databases"

    def _extract_database(self, obj):
        """Extract a database from the specified object."""

        assert isinstance(
            obj,
            (
                models.DatabaseCreateRequest,
                models.Database1,
                models.Database2,
                models.Database,
            ),
        )

        # Object mappings.
        if isinstance(obj, models.DatabaseCreateRequest):
            obj = obj.database.model_dump()
        if isinstance(obj, models.Database1):
            obj = obj.database.model_dump()
        if isinstance(obj, models.Database2):
            obj = obj.database.model_dump()
        if isinstance(obj, models.Database):
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
        )

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
        )

    def create(
        self,
        project_id: str,
        branch_id: str,
        db: models.DatabaseCreateRequest
        | models.Database1
        | models.Database2
        | models.Database,
    ):
        """Create a new database."""

        db = self._extract_database(db)

        return self.api.request(
            method="POST",
            path=self.api.url_join(
                "projects", project_id, "branches", branch_id, "databases"
            ),
            json=jsonable_encoder(DatabaseCreateRequest(database=db)),
            response_model=DatabaseResponse,
        )

    def update(
        self,
        project_id: str,
        branch_id: str,
        database_id: str,
        db: models.DatabaseUpdateRequest | models.Database2,
    ):
        """Update a database."""

        db = self._extract_database(db)

        return self.api.request(
            method="PATCH",
            path=self.api.url_join(
                "projects", project_id, "branches", branch_id, "databases", database_id
            ),
            json=models.DatabaseUpdateRequest(database=db).model_dump(),
            response_model=models.DatabaseResponse,
        )


class BranchResource(Resource):
    """A resource for interacting with branches."""

    path = "branches"

    def get_list(self, project_id: str):
        """Get a list of branches."""

        return self.api.request(
            method="GET",
            path=self.api.url_join("projects", project_id, "branches"),
            response_model=models.BranchesResponse,
        )

    def get(self, project_id: str, branch_id: str):
        """Get a branch."""

        return self.api.request(
            method="GET",
            path=self.api.url_join("projects", project_id, "branches", branch_id),
            response_model=models.BranchResponse,
        )

    def create(self, project_id: str, request: models.BranchCreateRequest):
        """Create a new branch."""

        return self.api.request(
            method="POST",
            path=self.api.url_join("projects", project_id, "branches"),
            json=request.model_dump(),
            response_model=models.BranchResponse,
        )


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
        )

    def get(self, project_id: str, operation_id: str):
        """Get an operation."""

        return self.api.request(
            method="GET",
            path=self.api.url_join("projects", project_id, "operations", operation_id),
            response_model=models.OperationResponse,
        )


class ResourceCollection:
    """A collection of resources."""

    def __init__(self, api: Neon_API_V2):
        """Initialize the collection."""

        # Initialize resources.
        self.api_keys = APIKeyResource(api)
        self.users = UserResource(api)
        self.projects = ProjectResource(api)
        self.databases = DatabaseResource(api)
        self.branches = BranchResource(api)
        self.operations = OperationResource(api)
