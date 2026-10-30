import json
from unittest.mock import MagicMock


from neon_api.client import NeonAPI


def _mock_response(payload):
    response = MagicMock()
    response.status_code = 200
    response.text = json.dumps(payload)
    response.json.return_value = payload
    response.raise_for_status = MagicMock()
    return response


def test_role_password_reveal_uses_get():
    client = NeonAPI("test-key")
    captured = {}

    def fake_request(method, url, **kwargs):
        captured["method"] = method
        captured["url"] = url
        return _mock_response({"password": "secret"})

    client._session.request = fake_request
    result = client.role_password_reveal("proj-1", "br-1", "owner")

    assert captured["method"] == "GET"
    assert captured["url"].endswith(
        "projects/proj-1/branches/br-1/roles/owner/reveal_password"
    )
    assert result.password == "secret"


def test_connection_uri_includes_branch_id_query_param():
    client = NeonAPI("test-key")
    captured = {}

    def fake_request(method, url, **kwargs):
        captured["method"] = method
        captured["url"] = url
        captured["params"] = kwargs.get("params")
        return _mock_response({"uri": "postgres://example"})

    client._session.request = fake_request
    result = client.connection_uri(
        "proj-1",
        database_name="neondb",
        role_name="neondb_owner",
        pooled=True,
        branch_id="br-dev",
    )

    assert captured["method"] == "GET"
    assert captured["params"]["branch_id"] == "br-dev"
    assert captured["params"]["database_name"] == "neondb"
    assert captured["params"]["role_name"] == "neondb_owner"
    assert captured["params"]["pooled"] is True
    assert result.uri == "postgres://example"
