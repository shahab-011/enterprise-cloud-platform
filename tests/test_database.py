from concurrent.futures import ThreadPoolExecutor

import pytest

from shared.database import DemoDatabase


def test_concurrent_database_operations_complete_and_close_connections(tmp_path):
    database = DemoDatabase(str(tmp_path / "concurrent.sqlite3"), timeout_seconds=5)
    database.initialize()

    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(lambda index: database.record_event("test", str(index)), range(40)))

    assert database.ping()
    assert database.event_count() == 40


def test_database_transaction_rolls_back_after_exception(tmp_path):
    database = DemoDatabase(str(tmp_path / "rollback.sqlite3"))
    database.initialize()

    with pytest.raises(RuntimeError, match="simulated failure"), database.connection() as connection:
        connection.execute(
            "INSERT INTO demo_events (event_type, request_id) VALUES (?, ?)",
            ("test", "request-1"),
        )
        raise RuntimeError("simulated failure")

    assert database.event_count() == 0
