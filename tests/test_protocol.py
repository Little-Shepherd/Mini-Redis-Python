"""Tests for RESP protocol encoding and decoding."""

import pytest
from src.protocol import (
    RESPDecoder, RESPSyntaxError,
    encode, encode_error, encode_bulk_string,
    encode_integer, encode_simple_string, encode_array,
    parse_command,
)


class TestEncode:
    def test_encode_simple_string(self):
        assert encode("OK") == b"+OK\r\n"

    def test_encode_error(self):
        assert encode_error("ERR msg") == b"-ERR ERR msg\r\n"

    def test_encode_integer(self):
        assert encode_integer(42) == b":42\r\n"

    def test_encode_bulk_string(self):
        assert encode_bulk_string("hello") == b"$5\r\nhello\r\n"

    def test_encode_null_string(self):
        assert encode(None) == b"$-1\r\n"

    def test_encode_array(self):
        arr = ["SET", "key", "value"]
        result = encode(arr)
        expected = b"*3\r\n+SET\r\n+key\r\n+value\r\n"
        assert result == expected


class TestDecode:
    def test_decode_simple_string(self):
        d = RESPDecoder(b"+OK\r\n")
        assert d.decode() == "OK"

    def test_decode_error(self):
        d = RESPDecoder(b"-ERR something\r\n")
        assert d.decode() == "ERR something"

    def test_decode_integer(self):
        d = RESPDecoder(b":100\r\n")
        assert d.decode() == 100

    def test_decode_bulk_string(self):
        d = RESPDecoder(b"$5\r\nhello\r\n")
        assert d.decode() == b"hello"

    def test_decode_null_bulk_string(self):
        d = RESPDecoder(b"$-1\r\n")
        assert d.decode() is None

    def test_decode_array(self):
        d = RESPDecoder(b"*2\r\n$4\r\nECHO\r\n$5\r\nhello\r\n")
        result = d.decode()
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0] == b"ECHO"
        assert result[1] == b"hello"

    def test_decode_empty(self):
        d = RESPDecoder(b"")
        with pytest.raises(RESPSyntaxError):
            d.decode()

    def test_decode_unknown_type(self):
        d = RESPDecoder(b"!bad\r\n")
        with pytest.raises(RESPSyntaxError):
            d.decode()


class TestParseCommand:
    def test_parse_simple(self):
        result = parse_command(b"*1\r\n$4\r\nPING\r\n")
        assert result == ["PING"]

    def test_parse_with_args(self):
        result = parse_command(b"*3\r\n$3\r\nSET\r\n$3\r\nkey\r\n$5\r\nvalue\r\n")
        assert result == ["SET", "key", "value"]
