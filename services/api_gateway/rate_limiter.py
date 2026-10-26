from collections import defaultdict, deque
from threading import Lock
from time import monotonic


class RateLimiter:
    def __init__(self, limit: int, window_seconds: int) -> None:
        if limit < 1:
            raise ValueError("limit must be at least 1")
        if window_seconds < 1:
            raise ValueError("window_seconds must be at least 1")
        self.limit = limit
        self.window_seconds = window_seconds
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str) -> tuple[bool, int]:
        now = monotonic()
        cutoff = now - self.window_seconds
        with self._lock:
            requests = self._requests[key]
            while requests and requests[0] <= cutoff:
                requests.popleft()
            if len(requests) >= self.limit:
                retry_after = max(1, int(requests[0] + self.window_seconds - now + 0.999))
                return False, retry_after
            requests.append(now)
            return True, 0
