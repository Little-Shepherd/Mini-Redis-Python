"""In-memory key-value store with TTL support and list operations.

Thread-safe via threading lock. Used by commands.py handler functions.
Store methods are synchronous — they are called from within an asyncio server
but do not themselves require await.
"""

import threading
import time
from typing import Any


class Store:
    def __init__(self):
        self._data: dict[str, Any] = {}
        self._expires: dict[str, float] = {}
        self._lock = threading.Lock()

    def _is_expired(self, key: str) -> bool:
        if key not in self._expires:
            return False
        return time.monotonic() >= self._expires[key]

    def _cleanup_expired(self, key: str) -> None:
        if self._is_expired(key):
            self._data.pop(key, None)
            self._expires.pop(key, None)

    def set(self, key: str, value: Any, ttl_ms: int | None = None) -> None:
        with self._lock:
            self._data[key] = value
            if ttl_ms is not None and ttl_ms > 0:
                self._expires[key] = time.monotonic() + ttl_ms / 1000.0
            else:
                self._expires.pop(key, None)

    def get(self, key: str) -> Any | None:
        with self._lock:
            self._cleanup_expired(key)
            return self._data.get(key)

    def delete(self, key: str) -> int:
        with self._lock:
            self._expires.pop(key, None)
            if key in self._data:
                del self._data[key]
                return 1
            return 0

    def exists(self, *keys: str) -> int:
        with self._lock:
            count = 0
            for key in keys:
                self._cleanup_expired(key)
                if key in self._data:
                    count += 1
            return count

    def keys(self, pattern: str = "*") -> list[str]:
        with self._lock:
            result = []
            for key in list(self._data.keys()):
                self._cleanup_expired(key)
                if key in self._data:
                    if pattern == "*" or self._match_pattern(key, pattern):
                        result.append(key)
            return result

    def expire(self, key: str, ttl_ms: int) -> int:
        with self._lock:
            if key not in self._data:
                return 0
            if ttl_ms > 0:
                self._expires[key] = time.monotonic() + ttl_ms / 1000.0
            else:
                self._expires.pop(key, None)
            return 1

    def ttl(self, key: str) -> int:
        with self._lock:
            self._cleanup_expired(key)
            if key not in self._data:
                return -2
            if key not in self._expires:
                return -1
            remaining = int((self._expires[key] - time.monotonic()) * 1000)
            return max(remaining, 0)

    def lpush(self, key: str, *values: str) -> int:
        with self._lock:
            if key not in self._data or not isinstance(self._data[key], list):
                self._data[key] = []
                self._expires.pop(key, None)
            lst = self._data[key]
            for v in reversed(values):
                lst.insert(0, v)
            return len(lst)

    def rpush(self, key: str, *values: str) -> int:
        with self._lock:
            if key not in self._data or not isinstance(self._data[key], list):
                self._data[key] = []
                self._expires.pop(key, None)
            lst = self._data[key]
            lst.extend(values)
            return len(lst)

    def lrange(self, key: str, start: int, stop: int) -> list:
        with self._lock:
            self._cleanup_expired(key)
            if key not in self._data or not isinstance(self._data[key], list):
                return []
            lst = self._data[key]
            length = len(lst)
            if start < 0:
                start = max(length + start, 0)
            if stop < 0:
                stop = length + stop
            return lst[start:stop + 1] if start <= stop else []

    def llen(self, key: str) -> int:
        with self._lock:
            self._cleanup_expired(key)
            if key not in self._data or not isinstance(self._data[key], list):
                return 0
            return len(self._data[key])

    @staticmethod
    def _match_pattern(key: str, pattern: str) -> bool:
        if "*" not in pattern and "?" not in pattern:
            return key == pattern
        import re
        regex = re.escape(pattern).replace(r"\*", ".*").replace(r"\?", ".")
        return re.fullmatch(regex, key) is not None
