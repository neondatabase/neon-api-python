import neon_client


def test_me(neon):
    me = neon.me()
    assert me


def test_get_projects(neon):
    projects = neon.get_projects()
    assert projects
