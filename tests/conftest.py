from random import randint

import pytest


@pytest.fixture
def neon():
    from neon_api import NeonAPI

    return NeonAPI.from_environ()


@pytest.fixture
def random_name(*, neon):
    def random_name():
        return f"pytest-{randint(0, 10000)}"

    return random_name


@pytest.fixture
def ensure_no_projects(*, neon):
    def no_projects():
        for project in neon.projects().projects:
            neon.project_delete(project.id)

    return no_projects
