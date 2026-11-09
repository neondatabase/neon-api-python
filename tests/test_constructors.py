import neon_api


def test_from_token_builds_a_client():
    neon = neon_api.from_token("an-api-key")

    assert isinstance(neon, neon_api.NeonAPI)
    assert neon.base_url == "https://console.neon.tech/api/v2/"


def test_from_environ_builds_a_client(monkeypatch):
    monkeypatch.setenv("NEON_API_KEY", "an-api-key")
    neon = neon_api.from_environ()

    assert isinstance(neon, neon_api.NeonAPI)
