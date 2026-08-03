"""Simple TCP server for Mini-Redis.

Listens on a configured host:port, accepts connections, reads RESP-encoded
commands, dispatches to commands.py handlers, and writes RESP-encoded replies.

Usage:
    python -m src.server [--host HOST] [--port PORT]
"""

import argparse
import asyncio
import logging

from src.protocol import CRLF, encode, encode_error, parse_command, RESPSyntaxError
from src.store import Store
from src.commands import dispatch_command

logger = logging.getLogger("mini-redis")


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, store: Store) -> None:
    addr = writer.get_extra_info("peername")
    logger.info(f"Client connected: {addr}")
    buf = bytearray()
    try:
        while True:
            chunk = await reader.read(4096)
            if not chunk:
                break
            buf.extend(chunk)
            while CRLF in buf:
                try:
                    command_data = parse_command(bytes(buf))
                    buf.clear()
                    result = dispatch_command(command_data, store)
                    response = encode(result)
                    writer.write(response)
                    await writer.drain()
                except RESPSyntaxError as e:
                    writer.write(encode_error(str(e)))
                    await writer.drain()
                except ValueError as e:
                    writer.write(encode_error(str(e)))
                    await writer.drain()
                except Exception as e:
                    logger.exception(f"Unexpected error handling command")
                    writer.write(encode_error(f"Internal error: {e}"))
                    await writer.drain()
                break
    except ConnectionResetError:
        pass
    except asyncio.CancelledError:
        pass
    finally:
        logger.info(f"Client disconnected: {addr}")
        writer.close()
        await writer.wait_closed()


async def run_server(host: str = "127.0.0.1", port: int = 6379) -> None:
    store = Store()
    server = await asyncio.start_server(
        lambda r, w: handle_client(r, w, store),
        host=host,
        port=port,
    )
    addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    logger.info(f"Mini-Redis listening on {addrs}")
    async with server:
        await server.serve_forever()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    parser = argparse.ArgumentParser(description="Mini-Redis Server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=6379)
    args = parser.parse_args()
    asyncio.run(run_server(host=args.host, port=args.port))


if __name__ == "__main__":
    main()
