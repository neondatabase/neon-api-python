from random import randint

import pytest
import neon_api


@pytest.fixture(scope="module")
def vcr_config():
    return {"filter_headers": ["authorization"]}


@pytest.mark.vcr
def test_me(neon):
    me = neon.me()

    assert isinstance(me, neon_api.schema.CurrentUserInfoResponse)
    assert me.email


@pytest.mark.vcr
def test_api_keys(neon, random_name):
    key = neon.api_key_create(key_name=random_name())

    assert len(neon.api_keys())

    key = neon.api_key_revoke(key.id)
    assert key.revoked


@pytest.mark.vcr
def test_project(neon, ensure_no_projects, random_name):
    # Ensure there are no projects.
    ensure_no_projects()

    # Create a project.
    project1 = neon.project_create(project={"name": random_name()}).project
    assert project1.id

    # Get the project.
    project = neon.project(project1.id).project
    assert project.id == project1.id

    # Rename the project.
    project2 = neon.project_update(project1.id, project={"name": random_name()}).project

    # Ensure that the names are different.
    assert project1.name != project2.name

    # Test Projects, ensure each project has an id.
    for project in neon.projects().projects:
        assert hasattr(project, "id")

    # Test Shared Projects, ensure each project has an id.
    for project in neon.projects(shared=True).projects:
        assert hasattr(project, "id")

    neon.connection_uri(project.id, "neondb", "neondb_owner", True)

    # Delete the project.
    neon.project_delete(project.id)


@pytest.mark.vcr
def test_branches(neon, ensure_no_projects, random_name):
    # Ensure there are no projects.
    ensure_no_projects()

    # Create a project.
    project = neon.project_create(project={"name": random_name()}).project
    assert project.id

    # import time

    # time.sleep(5)

    # Create a branch.
    # branch1 = neon.branch_create(project.id, branch={"name": random_name()}).branch
    # assert branch1.id

    # Rename the branch.
    # branch2 = neon.branch_update(branch1.id, branch={"name": random_name()}).branch
    # Ensure that the names are different.
    # assert branch2.name != branch1.name

    # Ensure that the IDs are present.
    # for i, branch in neon.branches(project.id).branches:
    # if i == 0:
    # Only set the first branch as primary.
    # neon.branch_set_as_primary(project.id, branch.id)
    # pass

    # List branches.
    neon.branches(project.id)
    # Delete the project.
    # neon.branch_delete(project.id, branch_id=neon.branches(project.id).branches[].id)


@pytest.mark.vcr
def test_database(neon, ensure_no_projects, random_name):
    # Ensure there are no projects.
    ensure_no_projects()

    # Create a project.
    project = neon.project_create(project={"name": random_name()}).project
    assert project.id

    branch = neon.branches(project.id).branches[0]

    # List databases.
    databases = neon.databases(project.id, branch.id).databases
    assert len(databases)

    # Create a database.
    # database = neon.database_create(
    #     project.id,
    #     branch.id,
    #     database={"name": random_name(), "owner_name": "kennethreitz"},
    # ).database

    # Get the Database.
    # database = neon.database(project.id, branch.id, database.id).database
    # assert database.id

    # # Rename the database.
    # database = neon.database_update(
    #     project.id,
    #     branch.id,
    #     database.id,
    #     database={"name": random_name()},
    # ).database


@pytest.mark.vcr
def test_operations(neon, ensure_no_projects, random_name):
    # Ensure there are no projects.
    ensure_no_projects()

    # Create a project.
    project = neon.project_create(project={"name": random_name()}).project
    assert project.id

    # Find the associated branch.
    branch = neon.branches(project.id).branches[0]

    # List operations.
    operations = neon.operations(project.id).operations
    assert len(operations)

    # Get the operation.
    operation = operations[0]
    operation = neon.operation(project.id, operation.id).operation
    assert operation.id


@pytest.mark.vcr
def test_endpoints(neon, ensure_no_projects, random_name):
    # Ensure there are no projects.
    ensure_no_projects()

    # Create a project.
    project = neon.project_create(project={"name": random_name()}).project
    assert project.id

    # List endpoints.
    endpoints = neon.endpoints(project.id).endpoints
    assert len(endpoints)

    # Get the endpoint.
    endpoint = endpoints[0]
    endpoint = neon.endpoint(project.id, endpoint.id).endpoint
    assert endpoint.id


@pytest.mark.vcr
def test_roles(neon, ensure_no_projects, random_name):
    # Ensure there are no projects.
    ensure_no_projects()

    # Create a project.
    project = neon.project_create(project={"name": random_name()}).project
    assert project.id

    # Find the associated branch.
    branch = neon.branches(project.id).branches[0]

    # List roles.
    roles = neon.roles(project.id, branch.id).roles
    assert len(roles)

    # Get the role.
    role = roles[0]
    role = neon.role(project.id, branch.id, role.name).role
    assert role.name
