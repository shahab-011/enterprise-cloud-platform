from fastapi.testclient import TestClient

from services.platform_api import create_app
from shared.config import Settings


def test_rate_limiter_rejects_excess_requests(tmp_path):
    settings = Settings(
        database_path=str(tmp_path / "gateway.sqlite3"),
        rate_limit_requests=1,
        rate_limit_window_seconds=60,
    )
    with TestClient(create_app(settings)) as client:
        first = client.get("/api/v1/routes")
        second = client.get("/api/v1/routes")

    assert first.status_code == 200
    assert second.status_code == 429
    assert second.headers["retry-after"]
    assert second.json()["error"]["code"] == "rate_limit_exceeded"


def test_routes_and_static_issue_fixtures_are_explicit(client):
    routes = client.get("/api/v1/routes")
    issues = client.get("/api/v1/demo/issues")

    assert routes.status_code == 200
    assert any(route["path"] == "/api/v1/auth/validate" for route in routes.json()["routes"])
    assert issues.json()["source"] == "static_fixture_not_live_jira"
    assert [issue["key"] for issue in issues.json()["issues"]] == [
        f"ECP-{number}" for number in range(1, 10)
    ]


def test_dashboard_is_responsive_and_served_locally(client):
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert "viewport" in response.text
    assert "@media (max-width: 640px)" in response.text
    assert "local metrics" in response.text.lower()


def test_openapi_documents_consistent_api_errors(client):
    specification = client.get("/openapi.json").json()

    responses = specification["paths"]["/api/v1/auth/validate"]["post"]["responses"]
    assert "401" in responses
    assert "422" in responses
    assert "ErrorResponse" in specification["components"]["schemas"]
