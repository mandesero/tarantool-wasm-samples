from wit_world import exports

import asyncio
import sys

from ssl_compat import install

install()

from websockets.asyncio.client import connect
from websockets.asyncio.server import serve

"".encode("idna")


async def roundtrip(port: int, text: str) -> None:
    async def echo(websocket) -> None:
        async with asyncio.timeout(10):
            message = await websocket.recv()
            if not isinstance(message, str):
                raise RuntimeError("expected a WebSocket text frame")
            await websocket.send(f"echo:{message}")

    async with serve(
        echo,
        "127.0.0.1",
        port,
        compression=None,
        ping_interval=None,
        close_timeout=5,
    ):
        async with connect(
            f"ws://127.0.0.1:{port}/echo",
            compression=None,
            proxy=None,
            ping_interval=None,
            open_timeout=5,
            close_timeout=5,
        ) as websocket:
            await websocket.send(text)
            async with asyncio.timeout(10):
                response = await websocket.recv()
            expected = f"echo:{text}"
            if response != expected:
                raise RuntimeError(f"WebSocket roundtrip mismatch: {response!r}")

    print(f"PYTHON WEBSOCKET ROUNDTRIP: {response}")


class Run(exports.Run):
    def run(self) -> None:
        if len(sys.argv) != 2:
            raise RuntimeError("expected arguments: PORT MESSAGE")
        asyncio.run(roundtrip(int(sys.argv[0]), sys.argv[1]))
