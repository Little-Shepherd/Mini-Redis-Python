# SPEC: Mini-Redis Command Implementation

## Overview

The `src/commands.py` file contains 8 command handler functions, each marked with `# TODO` and currently returning `pass`. Your task is to implement these functions so that all tests in `tests/test_commands.py` pass.

## Architecture Context

Each handler function receives:
- `data: list[str]` — the parsed command. `data[0]` is the command name (upper-cased).
- `store: Store` — the in-memory key-value store (see `src/store.py` for API).

A handler must return one of:
- `str` → encoded as Simple String (`+value\r\n`)
- `bytes` → encoded as Bulk String (`$N\r\n...\r\n`)
- `int` → encoded as Integer (`:value\r\n`)
- `list` → encoded as Array (`*N\r\n...`)
- `None` → encoded as Null Bulk String (`$-1\r\n`)

If a handler raises `ValueError`, the server returns `-ERR message\r\n`.

## Store API Reference

```python
store.set(key: str, value, ttl_ms: int | None = None) -> None
store.get(key: str) -> value | None
store.delete(key: str) -> int           # returns 1 if deleted, 0 if not found
store.exists(*keys: str) -> int         # returns count of existing keys
store.lpush(key: str, *values: str) -> int  # prepend values, returns new length
store.lrange(key: str, start: int, stop: int) -> list  # returns slice, empty if key missing
```

## Task List

### Group 1: Warm-up Commands (independent, no Store dependency)

#### Task 1-1: PING
- **Command**: `PING`
- **data**: `["PING"]`
- **Expected behavior**: Return the string `"PONG"`
- **check_items**:
  - Returns `"PONG"` as a string
  - Does not access the store

#### Task 1-2: ECHO
- **Command**: `ECHO message`
- **data**: `["ECHO", "hello world"]`
- **Expected behavior**: Return `data[1]` (the message string)
- **check_items**:
  - Returns the exact message string from data[1]
  - Works with empty string (`ECHO ""` returns `""`)

### Group 2: Key-Value Operations (depends on Store API understanding)

#### Task 2-1: SET
- **Command**: `SET key value [EX seconds]`
- **data**: `["SET", "key", "value"]` or `["SET", "key", "value", "EX", "10"]`
- **Expected behavior**: Call `store.set(key, value, ttl_ms)` and return `"OK"`
- **TTL handling**: If `EX` flag present, parse seconds as int, convert to milliseconds
- **check_items**:
  - `SET key value` → calls store.set(key, value), returns `"OK"`
  - `SET key value EX 10` → calls store.set(key, value, ttl_ms=10000), returns `"OK"`
  - Overwriting a key works correctly

#### Task 2-2: GET
- **Command**: `GET key`
- **data**: `["GET", "key"]`
- **Expected behavior**: Call `store.get(key)`, return the value or `None`
- **check_items**:
  - Existing key → returns value
  - Missing key → returns `None`
  - Values survive SET → GET round-trip

### Group 3: Key Management (can execute in parallel with Group 2 after Group 2 completes)

#### Task 3-1: DEL
- **Command**: `DEL key [key ...]`
- **data**: `["DEL", "key1", "key2", "key3"]`
- **Expected behavior**: Call `store.delete(key)` for each key, return total count deleted
- **check_items**:
  - Single key delete → returns 1 if existed, 0 if not
  - Multiple key delete → returns count of actually deleted keys
  - Deleted keys are no longer accessible via GET

#### Task 3-2: EXISTS
- **Command**: `EXISTS key [key ...]`
- **data**: `["EXISTS", "key1", "key2"]`
- **Expected behavior**: Call `store.exists(*keys)`, return the count
- **check_items**:
  - Single existing key → returns 1
  - Mix of existing and non-existing → returns count of existing
  - All non-existing → returns 0

### Group 4: List Operations (more complex, independent of Groups 2-3)

#### Task 4-1: LPUSH
- **Command**: `LPUSH key value [value ...]`
- **data**: `["LPUSH", "key", "a", "b", "c"]`
- **Expected behavior**: Call `store.lpush(key, *values)`, return the new list length
- **check_items**:
  - New list → creates list, returns count of values pushed
  - Multiple values maintained in correct LIFO order
  - Returns integer (list length)

#### Task 4-2: LRANGE
- **Command**: `LRANGE key start stop`
- **data**: `["LRANGE", "key", "0", "-1"]`
- **Expected behavior**: Convert start/stop to int, call `store.lrange(key, start, stop)`, return the list
- **check_items**:
  - Full range (0, -1) returns all elements
  - Slice (1, 2) returns partial range
  - Missing key returns empty list
  - Negative indices behave correctly

## Parallel Groups

```
Group 1 (PING, ECHO) ─────────────────────────────────┐
                                                         │
Group 2 (SET, GET) ──────────────┐                       │
                                   │                      │
Group 3 (DEL, EXISTS) ← depends on Group 2 for verifying │
                                                         │
Group 4 (LPUSH, LRANGE) ─────────────────────────────────┘
```

## Acceptance Criteria

1. `make test` passes all 23 test cases
2. Each handler's implementation fits the function's `check_items` listed above
3. No changes to `protocol.py`, `store.py`, `server.py`, or test files
