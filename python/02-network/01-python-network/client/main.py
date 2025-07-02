from wit_world import exports

import socket
import sys

"".encode("idna")


def exchange(port: int) -> None:
    with socket.create_connection(("127.0.0.1", port)) as client:
        client.sendall(b"Hello from Python WASM")
        echoed = client.recv(1024)
        if echoed != b"Hello from Python WASM":
            raise RuntimeError(f"unexpected echo: {echoed!r}")
        print(f"ECHO RESPONSE: {echoed.decode()}")

    with socket.create_connection(("127.0.0.1", port)) as client:
        client.sendall(b"STOP")
        if client.recv(1024) != b"BYE":
            raise RuntimeError("server did not acknowledge shutdown")


class Run(exports.Run):
    def run(self) -> None:
        exchange(int(sys.argv[0]) if sys.argv else 65432)
