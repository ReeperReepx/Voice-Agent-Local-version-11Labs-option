"""Redis session state storage.

Stores session state in Redis for persistence across service restarts.
Falls back to in-memory dict if Redis is not available.
"""

import json
import os
from typing import Optional


REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
SESSION_TTL = 3600  # 1 hour

_redis_client = None


def get_redis():
    """Get Redis client, connecting if necessary."""
    global _redis_client
    if _redis_client is not None:
        return _redis_client

    try:
        import redis
        _redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True,
        )
        _redis_client.ping()
        return _redis_client
    except Exception:
        return None


class RedisStore:
    """Redis-backed session store with in-memory fallback."""

    def __init__(self):
        self._fallback: dict[str, str] = {}
        self._redis = get_redis()

    @property
    def is_redis_available(self) -> bool:
        return self._redis is not None

    def set(self, key: str, value: dict, ttl: int = SESSION_TTL) -> None:
        """Store a value."""
        data = json.dumps(value)
        if self._redis:
            try:
                self._redis.setex(f"session:{key}", ttl, data)
                return
            except Exception:
                pass
        self._fallback[key] = data

    def get(self, key: str) -> Optional[dict]:
        """Retrieve a value."""
        if self._redis:
            try:
                data = self._redis.get(f"session:{key}")
                if data:
                    return json.loads(data)
            except Exception:
                pass
        data = self._fallback.get(key)
        return json.loads(data) if data else None

    def delete(self, key: str) -> None:
        """Delete a value."""
        if self._redis:
            try:
                self._redis.delete(f"session:{key}")
            except Exception:
                pass
        self._fallback.pop(key, None)

    def exists(self, key: str) -> bool:
        """Check if a key exists."""
        if self._redis:
            try:
                return self._redis.exists(f"session:{key}") > 0
            except Exception:
                pass
        return key in self._fallback
