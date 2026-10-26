import sqlite3
from collections.abc import Iterator
from contextlib import closing, contextmanager
from pathlib import Path


class DemoDatabase:
    def __init__(self, path: str, timeout_seconds: float = 5.0) -> None:
        self.path = path
        self.timeout_seconds = timeout_seconds

    def initialize(self) -> None:
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS demo_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    request_id TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute("PRAGMA journal_mode = WAL")

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(
            self.path,
            timeout=self.timeout_seconds,
        )
        try:
            connection.execute(f"PRAGMA busy_timeout = {int(self.timeout_seconds * 1000)}")
            with connection:
                yield connection
        finally:
            connection.close()

    def ping(self) -> bool:
        with self.connection() as connection:
            return connection.execute("SELECT 1").fetchone() == (1,)

    def record_event(self, event_type: str, request_id: str) -> None:
        with self.connection() as connection:
            connection.execute(
                "INSERT INTO demo_events (event_type, request_id) VALUES (?, ?)",
                (event_type, request_id),
            )

    def event_count(self) -> int:
        with closing(sqlite3.connect(self.path, timeout=self.timeout_seconds)) as connection:
            return int(connection.execute("SELECT COUNT(*) FROM demo_events").fetchone()[0])
