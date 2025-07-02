from wit_world import exports

import socket
import sys


def serve(port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("127.0.0.1", port))
        server.listen(4)
        print(f"READY 127.0.0.1:{port}", flush=True)
        while True:
            conn, addr = server.accept()
            with conn:
                data = conn.recv(1024)
                if not data:
                    continue
                if data == b"STOP":
                    conn.sendall(b"BYE")
                    return
                print(f"Received from {addr}: {data!r}")
                conn.sendall(data)


class Run(exports.Run):
    def run(self) -> None:
        serve(int(sys.argv[0]) if sys.argv else 65432)
