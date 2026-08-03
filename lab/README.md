# Mini-Redis-Python

A Redis-compatible in-memory database server implemented in Python, designed as a fill-in-the-blank educational lab project.

## Architecture

```
client (redis-cli / telnet)
    │  RESP protocol (text/binary)
    ▼
┌─────────────┐
│  server.py  │  TCP socket server, accepts connections
│  handle_    │  Reads RESP bytes, dispatches to commands.py
│  client()   │
└──────┬──────┘
       │  parsed command: ["SET", "key", "value"]
       ▼
┌──────────────┐
│ commands.py  │  Command handlers (8 commands, ~8 TODO gaps)
│  handle_*()  │  Each handler: extract params → call Store methods
└──────┬───────┘
       │  store.set(key, value)
       ▼
┌──────────────┐
│  store.py    │  Thread-safe in-memory KV store
│  Store       │  Supports: string values, TTL expiry, list types
└──────┬───────┘
       │  response value
       ▼
┌──────────────┐
│ protocol.py  │  RESP wire format encoder/decoder
│  encode()    │  Python objects ↔ RESP bytes
│  decode()    │
└──────────────┘
```

### Module Details

| Module | Lines | Status | Description |
|--------|-------|--------|-------------|
| `src/protocol.py` | ~200 | ✅ Complete | RESP protocol: simple strings, bulk strings, integers, arrays, errors |
| `src/store.py` | ~150 | ✅ Complete | In-memory store: `set/get/delete/exists`, TTL expiry, list operations |
| `src/commands.py` | ~120 | ❌ 8 TODOs | Command handler functions that call Store methods |
| `src/server.py` | ~80 | ✅ Complete | TCP server loop with RESP parsing and response encoding |

## Supported Commands

| Command | Syntax | Description |
|---------|--------|-------------|
| PING | `PING` | Returns PONG |
| ECHO | `ECHO message` | Returns the message |
| SET | `SET key value [EX seconds]` | Set a key to a value, with optional TTL |
| GET | `GET key` | Get the value of a key |
| DEL | `DEL key [key ...]` | Delete one or more keys |
| EXISTS | `EXISTS key [key ...]` | Count how many keys exist |
| LPUSH | `LPUSH key value [value ...]` | Prepend values to a list |
| LRANGE | `LRANGE key start stop` | Get a range of elements from a list |
