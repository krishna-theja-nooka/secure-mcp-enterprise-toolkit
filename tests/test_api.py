from fastapi.testclient import TestClient

from toolkit.api import create_app
from toolkit.config import Settings


def test_dashboard_health_and_security_headers(client):
    response = client.get("/")
    assert response.status_code == 200 and "GATEHOUSE" in response.text
    assert "frame-ancestors 'none'" in response.headers["content-security-policy"]
    assert client.get("/health").status_code == 200
    assert client.get("/ready").status_code == 200
    assert client.get("/api/metrics").status_code == 401
    assert client.get("/", headers={"Host": "evil.example"}).status_code == 400


def test_api_trace_and_input_validation(client):
    response = client.post("/api/tools/analytics", json={}, headers={"X-API-Key": "analyst"})
    assert response.status_code == 200
    assert response.headers["x-request-id"] == response.json()["trace_id"]
    assert (
        client.post(
            "/api/tools/analytics", json={"region": "Mars"}, headers={"X-API-Key": "analyst"}
        ).status_code
        == 422
    )
    assert client.post("/api/tools/analytics", content="x" * 9000).status_code == 413
    assert (
        client.post("/api/tools/decide", json={}, headers={"X-API-Key": "operator"}).status_code
        == 404
    )


def test_full_human_workflow(client, proposal):
    pending = client.post(
        "/api/tools/propose_ticket", json=proposal, headers={"X-API-Key": "operator"}
    )
    aid = pending.json()["data"]["approval_id"]
    assert (
        client.get("/api/approvals", headers={"X-API-Key": "analyst"}).json()["data"]["approvals"]
        == []
    )
    decision = client.post(
        f"/api/approvals/{aid}/decision",
        json={"decision": "approve"},
        headers={"X-API-Key": "approver"},
    )
    assert decision.status_code == 200
    assert (
        len(client.get("/api/tickets", headers={"X-API-Key": "analyst"}).json()["data"]["tickets"])
        == 1
    )


def test_no_keys_fails_closed(tmp_path):
    with TestClient(create_app(Settings(tmp_path / "empty.db", {}))) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/ready").status_code == 503
        assert client.get("/api/metrics", headers={"X-API-Key": "demo"}).status_code == 401
