import json
import logging
from io import StringIO

from shared.logging_config import JsonFormatter


def test_validate_active_demo_token(client):
    response = client.post(
        "/api/v1/auth/validate",
        json={"token": "demo-admin-token"},
        headers={"X-Request-ID": "test-trace_001"},
    )

    assert response.status_code == 200
    assert response.json()["valid"] is True
    assert response.json()["user"]["role"] == "admin"
    assert response.json()["request_id"] == response.headers["x-request-id"] == "test-trace_001"


def test_invalid_and_expired_tokens_have_consistent_error_shape(client):
    invalid = client.post("/api/v1/auth/validate", json={"token": "not-a-token"})
    expired = client.post("/api/v1/auth/validate", json={"token": "demo-expired-token"})

    assert invalid.status_code == expired.status_code == 401
    assert invalid.json()["error"]["code"] == "invalid_credentials"
    assert expired.json()["error"]["code"] == "credential_expired"
    assert invalid.json()["error"]["request_id"] == invalid.headers["x-request-id"]
    assert expired.json()["error"]["request_id"] == expired.headers["x-request-id"]
    assert "not-a-token" not in invalid.text


def test_malformed_and_empty_credentials_are_rejected(client):
    malformed = client.post("/api/v1/auth/validate", json={"token": 7})
    empty = client.post("/api/v1/auth/validate", json={"token": ""})
    missing = client.post("/api/v1/auth/validate", json={})

    assert all(response.status_code == 422 for response in (malformed, empty, missing))
    assert all(response.json()["error"]["code"] == "validation_error" for response in (malformed, empty, missing))
    assert malformed.json()["error"]["request_id"] == malformed.headers["x-request-id"]


def test_unsafe_request_id_is_replaced(client):
    response = client.get("/health", headers={"X-Request-ID": "unsafe trace id"})

    assert response.status_code == 200
    assert response.headers["x-request-id"] != "unsafe trace id"
    assert len(response.headers["x-request-id"]) == 36


def test_authenticated_user_and_admin_access(client):
    viewer = client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer demo-viewer-token"},
    )
    denied = client.get(
        "/api/v1/admin/status",
        headers={"Authorization": "Bearer demo-viewer-token"},
    )
    allowed = client.get(
        "/api/v1/admin/status",
        headers={"Authorization": "Bearer demo-admin-token"},
    )

    assert viewer.status_code == 200
    assert viewer.json()["user_id"] == "demo-viewer"
    assert denied.status_code == 403
    assert denied.json()["error"]["code"] == "permission_denied"
    assert allowed.status_code == 200


def test_operator_has_operations_access_but_viewer_does_not(client):
    operator = client.get(
        "/api/v1/operations/status",
        headers={"Authorization": "Bearer demo-operator-token"},
    )
    viewer = client.get(
        "/api/v1/operations/status",
        headers={"Authorization": "Bearer demo-viewer-token"},
    )

    assert operator.status_code == 200
    assert operator.json()["access"] == "operator"
    assert viewer.status_code == 403
    assert viewer.json()["error"]["code"] == "permission_denied"


def test_missing_or_malformed_bearer_header_is_rejected(client):
    missing = client.get("/api/v1/users/me")
    malformed = client.get("/api/v1/users/me", headers={"Authorization": "Basic abc"})

    assert missing.status_code == malformed.status_code == 401
    assert missing.json()["error"]["code"] == "authentication_required"
    assert malformed.json()["error"]["code"] == "authentication_required"


def test_authentication_credentials_are_not_in_structured_logs(client):
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setFormatter(JsonFormatter())
    logger = logging.getLogger("services.platform_api")
    logger.addHandler(handler)
    try:
        invalid_token = client.post(
            "/api/v1/auth/validate",
            json={"token": "sensitive-demo-token"},
            headers={"X-Request-ID": "auth-log-token-001"},
        )
        invalid_bearer = client.get(
            "/api/v1/users/me",
            headers={
                "Authorization": "Bearer sensitive-header-token",
                "X-Request-ID": "auth-log-header-002",
            },
        )
    finally:
        logger.removeHandler(handler)
        handler.close()

    log_lines = log_stream.getvalue().splitlines()
    records = [json.loads(line) for line in log_lines]

    assert invalid_token.status_code == invalid_bearer.status_code == 401
    assert "sensitive-demo-token" not in log_stream.getvalue()
    assert "sensitive-header-token" not in log_stream.getvalue()
    assert {record["request_id"] for record in records} == {
        "auth-log-token-001",
        "auth-log-header-002",
    }
