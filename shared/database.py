import sqlite3
from collections.abc import Iterator
from contextlib import closing, contextmanager
from pathlib import Path
from uuid import uuid4


class DemoDatabase:
    def __init__(self, path: str, timeout_seconds: float = 5.0) -> None:
        self.path = path
        self.timeout_seconds = timeout_seconds
        self._uri = path == ":memory:"
        self._connect_path = (
            f"file:ecp-demo-{uuid4().hex}?mode=memory&cache=shared"
            if self._uri
            else path
        )
        self._anchor: sqlite3.Connection | None = None

    def initialize(self) -> None:
        if self._uri and self._anchor is None:
            self._anchor = sqlite3.connect(
                self._connect_path,
                timeout=self.timeout_seconds,
                uri=True,
            )
        elif not self._uri:
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        try:
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
        except sqlite3.Error:
            self.close()
            raise

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(
            self._connect_path,
            timeout=self.timeout_seconds,
            uri=self._uri,
        )
        try:
            connection.execute(f"PRAGMA busy_timeout = {int(self.timeout_seconds * 1000)}")
            with connection:
                yield connection
        finally:
            connection.close()

    def close(self) -> None:
        if self._anchor is not None:
            self._anchor.close()
            self._anchor = None

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
        with closing(
            sqlite3.connect(
                self._connect_path,
                timeout=self.timeout_seconds,
                uri=self._uri,
            )
        ) as connection:
            return int(connection.execute("SELECT COUNT(*) FROM demo_events").fetchone()[0])
