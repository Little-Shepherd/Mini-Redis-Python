"""Command handler functions for Mini-Redis.

Each handler receives:
  - data: the parsed command as a list of strings. data[0] is the command name (upper-cased).
  - store: the Store instance for data operations.

A handler must return a value compatible with protocol.encode():
  - str: will be encoded as a Simple String (+)
  - bytes: will be encoded as a Bulk String ($)
  - int: will be encoded as an Integer (:)
  - list: will be encoded as an Array (*)
  - None: will be encoded as a Null Bulk String ($-1)

If a handler raises ValueError, the server returns -ERR with the message.

COMMANDS BELOW WITH # TODO MARKERS ARE INCOMPLETE AND REQUIRE IMPLEMENTATION.
"""

from src.store import Store


def handle_ping(data: list[str], store: Store) -> str:
    # TODO: implement me
    raise NotImplementedError("handle_ping not implemented")


def handle_echo(data: list[str], store: Store) -> str:
    # TODO: implement me
    raise NotImplementedError("handle_echo not implemented")


def handle_set(data: list[str], store: Store) -> str:
    # TODO: implement me
    # SET key value → store.set(key, value); return "OK"
    # SET key value EX seconds → compute ttl_ms, store.set(key, value, ttl_ms)
    raise NotImplementedError("handle_set not implemented")


def handle_get(data: list[str], store: Store) -> str | None:
    # TODO: implement me
    raise NotImplementedError("handle_get not implemented")


def handle_del(data: list[str], store: Store) -> int:
    # TODO: implement me
    raise NotImplementedError("handle_del not implemented")


def handle_exists(data: list[str], store: Store) -> int:
    # TODO: implement me
    raise NotImplementedError("handle_exists not implemented")


def handle_lpush(data: list[str], store: Store) -> int:
    # TODO: implement me
    raise NotImplementedError("handle_lpush not implemented")


def handle_lrange(data: list[str], store: Store) -> list:
    # TODO: implement me
    raise NotImplementedError("handle_lrange not implemented")


# ---- Command Registry ----

COMMANDS: dict[str, callable] = {
    "PING": handle_ping,
    "ECHO": handle_echo,
    "SET": handle_set,
    "GET": handle_get,
    "DEL": handle_del,
    "EXISTS": handle_exists,
    "LPUSH": handle_lpush,
    "LRANGE": handle_lrange,
}


def dispatch_command(data: list[str], store: Store):
    """Look up and execute the appropriate handler.

    Returns the handler's return value.

    Raises ValueError for unknown commands or parameter errors.
    """
    if not data:
        raise ValueError("Empty command")
    cmd = data[0]
    if cmd not in COMMANDS:
        raise ValueError(f"Unknown command '{cmd}'")
    handler = COMMANDS[cmd]
    return handler(data, store)
