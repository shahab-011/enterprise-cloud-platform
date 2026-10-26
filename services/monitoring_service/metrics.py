from collections import Counter
from threading import Lock


class Metrics:
    def __init__(self) -> None:
        self._lock = Lock()
        self._total_requests = 0
        self._error_count = 0
        self._total_response_time_ms = 0.0
        self._requests_by_path: Counter[str] = Counter()

    def record(self, path: str, status_code: int, response_time_ms: float) -> None:
        with self._lock:
            self._total_requests += 1
            self._error_count += status_code >= 400
            self._total_response_time_ms += response_time_ms
            self._requests_by_path[path] += 1

    def snapshot(self) -> dict[str, object]:
        with self._lock:
            average = (
                self._total_response_time_ms / self._total_requests
                if self._total_requests
                else 0.0
            )
            return {
                "source": "local_process",
                "total_requests": self._total_requests,
                "error_count": self._error_count,
                "average_response_time_ms": round(average, 3),
                "requests_by_path": dict(sorted(self._requests_by_path.items())),
            }
