from random import randint

import pytest


@pytest.fixture
def neon():
    from neon_client import NeonAPI

    return NeonAPI.from_environ()


@pytest.fixture
def ensure_project(find_existing=True, *, neon):
    def new_project():
        # Return main project if it exists.
        if neon.projects().projects:
            return neon.projects().projects[0]

        return neon.project_create(project={"name": f"pytest-{randint(0, 1000)}"})

    return new_project


@pytest.fixture
def ensure_new_api_key(*, neon):
    def new_api_key():
        return neon.api_key_create(key_name=f"pytest-{randint(0, 1000)}")

    return new_api_key
