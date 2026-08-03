"""Tests for in-memory Store operations."""

import time
import pytest
from src.store import Store


@pytest.fixture
def store():
    return Store()


class TestStoreBasics:
    def test_set_and_get(self, store):
        store.set("key1", "value1")
        assert store.get("key1") == "value1"

    def test_get_missing(self, store):
        assert store.get("no_such_key") is None

    def test_overwrite(self, store):
        store.set("key1", "first")
        store.set("key1", "second")
        assert store.get("key1") == "second"

    def test_delete(self, store):
        store.set("key1", "value1")
        assert store.delete("key1") == 1
        assert store.get("key1") is None

    def test_delete_missing(self, store):
        assert store.delete("no_such_key") == 0

    def test_exists(self, store):
        store.set("a", "1")
        store.set("b", "2")
        assert store.exists("a", "b", "c") == 2

    def test_exists_none(self, store):
        assert store.exists("x") == 0


class TestStoreTTL:
    def test_set_with_ttl(self, store):
        store.set("key1", "value1", ttl_ms=500)
        assert store.get("key1") == "value1"

    def test_ttl_expiry(self, store):
        store.set("key1", "value1", ttl_ms=50)
        time.sleep(0.1)
        assert store.get("key1") is None

    def test_ttl_overwrite_removes_expiry(self, store):
        store.set("key1", "value1", ttl_ms=500)
        store.set("key1", "value2")
        assert store.ttl("key1") == -1


class TestStoreLists:
    def test_lpush_empty_key(self, store):
        length = store.lpush("mylist", "a")
        assert length == 1

    def test_lpush_multiple(self, store):
        length = store.lpush("mylist", "a", "b", "c")
        assert length == 3

    def test_lpush_order(self, store):
        store.lpush("mylist", "a")
        store.lpush("mylist", "b")
        result = store.lrange("mylist", 0, -1)
        assert result == ["b", "a"]

    def test_rpush_order(self, store):
        store.rpush("mylist", "a")
        store.rpush("mylist", "b")
        result = store.lrange("mylist", 0, -1)
        assert result == ["a", "b"]

    def test_lrange_slice(self, store):
        store.rpush("mylist", "a", "b", "c", "d")
        assert store.lrange("mylist", 1, 2) == ["b", "c"]

    def test_lrange_negative_index(self, store):
        store.rpush("mylist", "a", "b", "c")
        assert store.lrange("mylist", -2, -1) == ["b", "c"]

    def test_lrange_missing_key(self, store):
        assert store.lrange("no_such_list", 0, -1) == []

    def test_llen(self, store):
        store.rpush("mylist", "a", "b", "c")
        assert store.llen("mylist") == 3

    def test_llen_missing_key(self, store):
        assert store.llen("no_such_list") == 0
