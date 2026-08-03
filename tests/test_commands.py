"""Integration tests for command handlers.

These tests call dispatch_command() directly with pre-parsed command data.
Before implementing commands.py handlers, all tests FAIL (RED).
After correct implementation, all tests PASS (GREEN).

Run with:  make test
"""

import time

import pytest
from src.store import Store
from src.commands import dispatch_command


@pytest.fixture
def store():
    return Store()


class TestPing:
    def test_ping_returns_pong(self, store):
        result = dispatch_command(["PING"], store)
        assert result == "PONG"


class TestEcho:
    def test_echo_returns_message(self, store):
        result = dispatch_command(["ECHO", "hello world"], store)
        assert result == "hello world"

    def test_echo_empty(self, store):
        result = dispatch_command(["ECHO", ""], store)
        assert result == ""


class TestSetGet:
    def test_set_returns_ok(self, store):
        result = dispatch_command(["SET", "name", "Alice"], store)
        assert result == "OK"

    def test_get_existing_key(self, store):
        dispatch_command(["SET", "name", "Alice"], store)
        result = dispatch_command(["GET", "name"], store)
        assert result == "Alice"

    def test_get_missing_key_returns_none(self, store):
        result = dispatch_command(["GET", "missing"], store)
        assert result is None

    def test_set_overwrites(self, store):
        dispatch_command(["SET", "name", "Alice"], store)
        dispatch_command(["SET", "name", "Bob"], store)
        result = dispatch_command(["GET", "name"], store)
        assert result == "Bob"

    def test_set_with_ex_ttl(self, store):
        dispatch_command(["SET", "temp", "value", "EX", "1"], store)
        assert dispatch_command(["GET", "temp"], store) == "value"
        time.sleep(1.2)
        assert dispatch_command(["GET", "temp"], store) is None


class TestDel:
    def test_del_existing_key(self, store):
        dispatch_command(["SET", "key1", "v1"], store)
        result = dispatch_command(["DEL", "key1"], store)
        assert result == 1
        assert dispatch_command(["GET", "key1"], store) is None

    def test_del_missing_key(self, store):
        result = dispatch_command(["DEL", "missing"], store)
        assert result == 0

    def test_del_multiple_keys(self, store):
        dispatch_command(["SET", "a", "1"], store)
        dispatch_command(["SET", "b", "2"], store)
        dispatch_command(["SET", "c", "3"], store)
        result = dispatch_command(["DEL", "a", "b", "x"], store)
        assert result == 2
        assert dispatch_command(["EXISTS", "c"], store) == 1


class TestExists:
    def test_exists_one(self, store):
        dispatch_command(["SET", "key1", "v1"], store)
        assert dispatch_command(["EXISTS", "key1"], store) == 1

    def test_exists_multiple(self, store):
        dispatch_command(["SET", "a", "1"], store)
        dispatch_command(["SET", "b", "2"], store)
        assert dispatch_command(["EXISTS", "a", "b", "c"], store) == 2

    def test_exists_none(self, store):
        assert dispatch_command(["EXISTS", "x"], store) == 0


class TestListPush:
    def test_lpush_new_list(self, store):
        result = dispatch_command(["LPUSH", "queue", "a"], store)
        assert result == 1

    def test_lpush_multiple(self, store):
        result = dispatch_command(["LPUSH", "queue", "a", "b", "c"], store)
        assert result == 3

    def test_lpush_order(self, store):
        dispatch_command(["LPUSH", "queue", "a"], store)
        dispatch_command(["LPUSH", "queue", "b"], store)
        items = dispatch_command(["LRANGE", "queue", "0", "-1"], store)
        assert items == ["b", "a"]


class TestListRange:
    def test_lrange_empty_list(self, store):
        result = dispatch_command(["LRANGE", "empty", "0", "-1"], store)
        assert result == []

    def test_lrange_full_range(self, store):
        dispatch_command(["LPUSH", "queue", "c", "b", "a"], store)
        result = dispatch_command(["LRANGE", "queue", "0", "-1"], store)
        assert result == ["a", "b", "c"]

    def test_lrange_slice(self, store):
        dispatch_command(["LPUSH", "queue", "d", "c", "b", "a"], store)
        result = dispatch_command(["LRANGE", "queue", "1", "2"], store)
        assert result == ["b", "c"]

    def test_lrange_negative_index(self, store):
        dispatch_command(["LPUSH", "queue", "c", "b", "a"], store)
        result = dispatch_command(["LRANGE", "queue", "-2", "-1"], store)
        assert result == ["b", "c"]
