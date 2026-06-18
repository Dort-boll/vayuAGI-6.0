"""Simple Token Bucket Rate Limiter."""
from __future__ import annotations
import time
from ..config import CONFIG
from ..exceptions import RateLimitError
from ..logger import get_logger

log = get_logger("ratelimit")

class RateLimiter:
    def __init__(self):
        self.limit = CONFIG.rate_limit_per_min
        self.window = 60.0
        self._timestamps: list[float] = []

    def check(self) -> None:
        now = time.time()
        self._timestamps = [t for t in self._timestamps if now - t < self.window]
        if len(self._timestamps) >= self.limit:
            raise RateLimitError(f"Rate limit exceeded: {self.limit} requests per {self.window}s")
        self._timestamps.append(now)

RATE_LIMITER = RateLimiter()
