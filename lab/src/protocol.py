"""RESP (REdis Serialization Protocol) parser and serializer.

Supports:
- Simple Strings: +OK\r\n
- Errors: -ERR message\r\n
- Integers: :1000\r\n
- Bulk Strings: $5\r\nhello\r\n
- Arrays: *2\r\n$4\r\nECHO\r\n$5\r\nhello\r\n
- Null Bulk String: $-1\r\n
"""

import io
from typing import Any

CRLF = b"\r\n"
CRLF_STR = "\r\n"


class RESPSyntaxError(Exception):
    pass


def encode(value: Any) -> bytes:
    if isinstance(value, str):
        return f"+{value}{CRLF_STR}".encode()
    if isinstance(value, bytes):
        return b"$" + str(len(value)).encode() + CRLF + value + CRLF
    if isinstance(value, int):
        return f":{value}{CRLF_STR}".encode()
    if isinstance(value, list):
        parts = [f"*{len(value)}{CRLF_STR}".encode()]
        for item in value:
            parts.append(encode(item))
        return b"".join(parts)
    if value is None:
        return b"$-1\r\n"
    raise TypeError(f"Unsupported type: {type(value)}")


def encode_error(msg: str) -> bytes:
    return f"-ERR {msg}{CRLF_STR}".encode()


def encode_bulk_string(data: str | bytes) -> bytes:
    if isinstance(data, str):
        data = data.encode()
    return b"$" + str(len(data)).encode() + CRLF + data + CRLF


def encode_null_bulk_string() -> bytes:
    return b"$-1\r\n"


def encode_integer(n: int) -> bytes:
    return f":{n}{CRLF_STR}".encode()


def encode_simple_string(s: str) -> bytes:
    return f"+{s}{CRLF_STR}".encode()


def encode_array(items: list) -> bytes:
    parts = [f"*{len(items)}{CRLF_STR}".encode()]
    for item in items:
        parts.append(encode(item))
    return b"".join(parts)


class RESPDecoder:
    def __init__(self, data: bytes):
        self._reader = io.BytesIO(data)

    def decode(self) -> Any:
        byte = self._reader.read(1)
        if not byte:
            raise RESPSyntaxError("Unexpected end of stream")
        char = byte.decode()
        if char == "+":
            return self._read_simple_string()
        if char == "-":
            return self._read_error()
        if char == ":":
            return self._read_integer()
        if char == "$":
            return self._read_bulk_string()
        if char == "*":
            return self._read_array()
        raise RESPSyntaxError(f"Unknown type byte: {char!r}")

    def _read_line(self) -> bytes:
        line = bytearray()
        while True:
            byte = self._reader.read(1)
            if not byte:
                raise RESPSyntaxError("Unexpected end of stream in line")
            if byte == b"\r":
                next_byte = self._reader.read(1)
                if next_byte != b"\n":
                    raise RESPSyntaxError("Expected LF after CR")
                return bytes(line)
            line.append(byte[0])

    def _read_simple_string(self) -> str:
        return self._read_line().decode()

    def _read_error(self) -> str:
        return self._read_line().decode()

    def _read_integer(self) -> int:
        line = self._read_line().decode()
        return int(line)

    def _read_bulk_string(self) -> bytes | None:
        length = int(self._read_line().decode())
        if length == -1:
            return None
        data = self._reader.read(length)
        crlf = self._reader.read(2)
        if crlf != CRLF:
            raise RESPSyntaxError("Expected CRLF after bulk string")
        return data

    def _read_array(self) -> list:
        count = int(self._read_line().decode())
        if count == -1:
            return None
        items = []
        for _ in range(count):
            items.append(self.decode())
        return items


def parse_command(data: bytes) -> list[str]:
    decoder = RESPDecoder(data)
    result = decoder.decode()
    if isinstance(result, list):
        items = [item.decode() if isinstance(item, bytes) else str(item) for item in result]
        if items:
            items[0] = items[0].upper()
        return items
    if isinstance(result, bytes):
        return [result.decode().upper()]
    if isinstance(result, str):
        return [result.upper()]
    return [str(result)]
