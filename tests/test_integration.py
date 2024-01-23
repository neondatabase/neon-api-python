from random import randint

import pytest
import neon_client


@pytest.fixture(scope="module")
def vcr_config():
    return {"filter_headers": ["authorization"]}


@pytest.mark.vcr
def test_me(neon):
    me = neon.me()

    assert isinstance(me, neon_client.schema.CurrentUserInfoResponse)
    assert me.email


@pytest.mark.vcr
def test_api_keys(neon, random_name):
    key = neon.api_key_create(key_name=random_name())

    assert len(neon.api_keys())

    key = neon.api_key_revoke(key.id)
    assert key.revoked


@pytest.mark.vcr
def test_project(neon, ensure_no_projects, random_name):
    ensure_no_projects()

    project1 = neon.project_create(project={"name": random_name()}).project
    assert project1.id

    project2 = neon.project_update(
        project1.id, project={"name": "pytest-renamed"}
    ).project

    assert project1.name != project2.name

    for project in neon.projects().projects:
        assert hasattr(project, "id")

    neon.project_delete(project.id)


# @pytest.mark.vcr
# def test_update_project(neon, ensure_project):
#     project = ensure_project()

#     project_update = {"project": {"name": "pytest-renamed"}}

#     # r = neon.project_update(, **project_update)
#     assert r.project.name == "pytest-renamed"


# @pytest.mark.vcr
# def test_project_delete(neon, ensure_project):
#     r = ensure_project()
#     print(r)
#     exit()
#     r = neon.project_delete(r.id)
