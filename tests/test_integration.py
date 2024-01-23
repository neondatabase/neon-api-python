import pytest
import neon_client


@pytest.mark.vcr
def test_me(neon):
    me = neon.me()
    assert me["email"] == "me@kennethreitz.org"


@pytest.mark.vcr
@pytest.mark.vcr
def test_get_projects(neon):
    projects = neon.projects()
    assert "projects" in projects
