import pytest
from fastapi.testclient import TestClient

from services.platform_api import create_app
from shared.config import Settings


@pytest.fixture
def client(tmp_path):
    settings = Settings(database_path=str(tmp_path / "test.sqlite3"))
    with TestClient(create_app(settings)) as test_client:
        yield test_client
