import random

import pytest
import neon_client


@pytest.fixture(scope="module")
def vcr_config():
    return {"filter_headers": ["authorization"]}


@pytest.mark.vcr
def test_me(neon):
    me = neon.me()

    assert isinstance(me, neon_client.schema.CurrentUserInfoResponse)
    assert me.email == "me@kennethreitz.org"


@pytest.mark.vcr
def test_api_keys(neon, ensure_new_api_key):
    key = ensure_new_api_key()

    keys = neon.api_keys()
    assert len(keys)

    key = neon.api_key_revoke(key.id)
    assert key.revoked


@pytest.mark.vcr
def test_project(neon, ensure_project):
    project = ensure_project()

    for project in neon.projects().projects:
        assert hasattr(project, "id")


@pytest.mark.vcr
def test_get_project(neon, ensure_project):
    r = ensure_project()
    assert neon.project(r.id).project.id == r.id


# @pytest.mark.vcr
# def test_create_project(neon, ensure_project):
#     r = ensure_project()

#     project_update = {"project": {"name": "pytest-renamed"}}

#     r = neon.project_update(r.id, **project_update)
#     assert r.name == "pytest"


@pytest.mark.vcr
def test_update_project(neon, ensure_project):
    r = ensure_project()

    project_update = {"project": {"name": "pytest-renamed"}}

    r = neon.project_update(r.id, **project_update)
    assert r.project.name == "pytest-renamed"


# @pytest.mark.vcr
# def test_project_delete(neon, ensure_project):
#     r = ensure_project()
#     print(r)
#     exit()
#     r = neon.project_delete(r.id)
