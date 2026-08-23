from fastapi.testclient import TestClient

from ktrader.api.app import create_app


def test_bearer_key_guards_v1_but_health_stays_public():
    client = TestClient(create_app(action_api_key="top-secret"))
    assert client.get("/health").status_code == 200
    assert client.get("/health").json()["action_auth_enabled"] is True
    assert client.get("/v1/scanner/status").status_code == 401
    assert client.get("/v1/scanner/status", headers={"Authorization": "Bearer wrong"}).status_code == 401
    response = client.get("/v1/scanner/status", headers={"Authorization": "Bearer top-secret"})
    assert response.status_code == 200


def test_privacy_policy_is_public_but_not_an_action():
    client = TestClient(create_app(action_api_key="top-secret"))
    response = client.get("/privacy")
    assert response.status_code == 200
    assert "read-only" in response.text
    assert "/privacy" not in client.get("/openapi.json").json()["paths"]
