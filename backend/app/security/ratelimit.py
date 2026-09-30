"""Fixed-window rate limiter. Uses Redis when REDIS_URL is set (shared across workers/instances),
otherwise an in-process store (fine for dev/tests, NOT for multi-worker production)."""
import threading
import time

from fastapi import HTTPException, Request

from ..config import get_settings


class _MemoryStore:
    def __init__(self) -> None:
        self._data: dict[str, tuple[int, float]] = {}
        self._lock = threading.Lock()

    def hit(self, key: str, window: int) -> int:
        now = time.monotonic()
        with self._lock:
            count, reset = self._data.get(key, (0, now + window))
            if now >= reset:
                count, reset = 0, now + window
            count += 1
            self._data[key] = (count, reset)
            if len(self._data) > 100_000:  # bound memory under a flood of unique keys
                self._data = {k: v for k, v in self._data.items() if v[1] > now}
            return count

    def reset(self) -> None:
        with self._lock:
            self._data.clear()


class _RedisStore:
    def __init__(self, url: str) -> None:
        import redis

        self._r = redis.Redis.from_url(url, socket_timeout=0.5, socket_connect_timeout=0.5)

    def hit(self, key: str, window: int) -> int:
        bucket = f"rl:{key}:{int(time.time() // window)}"
        pipe = self._r.pipeline()
        pipe.incr(bucket)
        pipe.expire(bucket, window + 1)
        count, _ = pipe.execute()
        return int(count)

    def reset(self) -> None:  # pragma: no cover - test helper only
        pass


_store = None


def store():
    global _store
    if _store is None:
        url = get_settings().redis_url
        _store = _RedisStore(url) if url else _MemoryStore()
    return _store


def client_ip(request: Request) -> str:
    # uvicorn's --proxy-headers/--forwarded-allow-ips resolves X-Forwarded-For ONLY from trusted
    # proxies, so request.client is the real client and cannot be spoofed by a header.
    return request.client.host if request.client else "unknown"


def check(key: str, limit: int, window: int) -> tuple[bool, int]:
    """Returns (allowed, retry_after_seconds). Fails open if Redis is unreachable so an
    outage of the limiter cannot take the whole site down (nginx limits still apply)."""
    try:
        count = store().hit(key, window)
    except Exception:
        return True, 0
    return count <= limit, window


def limit(scope: str, limit_: int, window: int = 60, per: str = "ip"):
    """FastAPI dependency factory: `Depends(limit("auth", 10))`."""

    def dependency(request: Request) -> None:
        ident = client_ip(request)
        if per == "user" and getattr(request.state, "user_id", None):
            ident = f"u{request.state.user_id}"
        allowed, retry = check(f"{scope}:{ident}", limit_, window)
        if not allowed:
            raise HTTPException(429, "Too many requests. Please slow down.", headers={"Retry-After": str(retry)})

    return dependency
