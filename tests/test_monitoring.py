import sqlite3

from fastapi.testclient import TestClient

from services.platform_api import create_app
from shared.config import Settings
from shared.database import DemoDatabase


def test_health_and_process_local_metrics(client):
    health = client.get("/health")
    client.post("/api/v1/auth/validate", json={"token": "invalid"})
    metrics = client.get("/api/v1/metrics")

    assert health.status_code == 200
    assert health.json() == {
        "status": "healthy",
        "services": {"api": "healthy", "database": "healthy"},
    }
    snapshot = metrics.json()
    assert snapshot["source"] == "local_process"
    assert snapshot["total_requests"] == 2
    assert snapshot["error_count"] == 1
    assert snapshot["average_response_time_ms"] >= 0
    assert snapshot["requests_by_path"]["/health"] == 1


def test_health_reports_database_failure_as_degraded(tmp_path):
    class UnavailableDatabase(DemoDatabase):
        def ping(self) -> bool:
            raise sqlite3.OperationalError("simulated database outage")

    database = UnavailableDatabase(str(tmp_path / "unavailable.sqlite3"))
    settings = Settings(database_path=str(tmp_path / "unavailable.sqlite3"))
    with TestClient(create_app(settings, database)) as client:
        response = client.get("/health")

    assert response.status_code == 503
    assert response.json() == {
        "status": "degraded",
        "services": {"api": "healthy", "database": "unavailable"},
    }
