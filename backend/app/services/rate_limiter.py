import time
from collections import defaultdict, deque


class RateLimiter:
    """Allows `max_requests` per `window_seconds` for each key (for example an IP address).

    It is kept in memory: simple, but it resets when the server restarts.
    """

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, deque] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        hits = self._hits[key]
        while hits and now - hits[0] > self.window_seconds:
            hits.popleft()  # forget requests that are outside the window
        if len(hits) >= self.max_requests:
            return False
        hits.append(now)
        return True

    def reset(self) -> None:
        self._hits.clear()