from wit_world import exports

import sys
import types

from pbkdf2_compat import install
from wasi_tls_socket import WasiTlsContext, connect

install()

# pg8000 imports ssl even when the caller supplies a context. The actual
# context below is backed by wasi:tls; this module only satisfies that import.
sys.modules.setdefault("ssl", types.ModuleType("ssl"))

import pg8000.dbapi
import pg8000.core

"".encode("idna")


def roundtrip(
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
    text: str,
    tls_server_name: str,
) -> None:
    raw_socket = connect(host, port, 10)
    # wasi:tls draft does not expose the peer certificate needed for
    # tls-server-end-point channel binding. SCRAM without PLUS remains
    # available and the TLS certificate itself is still host-validated.
    pg8000.core.scramp.make_channel_binding = lambda _name, _sock: None

    try:
        connection = pg8000.dbapi.connect(
            user=user,
            password=password,
            database=database,
            host=host,
            port=port,
            timeout=10,
            sock=raw_socket,
            ssl_context=WasiTlsContext(tls_server_name),
        )
    except Exception:
        raw_socket.close()
        raise
    cursor = connection.cursor()
    try:
        cursor.execute(
            "CREATE TEMPORARY TABLE tarawasm_messages ("
            "id BIGSERIAL PRIMARY KEY, body TEXT NOT NULL)"
        )
        cursor.execute(
            "INSERT INTO tarawasm_messages (body) VALUES (%s) RETURNING id",
            (text,),
        )
        inserted_id = cursor.fetchone()[0]
        connection.commit()

        cursor.execute(
            "SELECT body FROM tarawasm_messages WHERE id = %s",
            (inserted_id,),
        )
        received = cursor.fetchone()[0]
        if received != text:
            raise RuntimeError(f"PostgreSQL roundtrip mismatch: {received!r}")
        print(f"PYTHON PG8000 ROUNDTRIP: id={inserted_id} body={received}")
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def tls_probe(host: str, port: int, server_name: str) -> None:
    sock = connect(host, port, 10)
    try:
        sock.start_tls(server_name)
        sock.sendall(
            (
                f"GET / HTTP/1.1\r\nHost: {server_name}\r\n"
                "Connection: close\r\n\r\n"
            ).encode("ascii")
        )
        response = sock.recv(4096)
        if not response.startswith(b"HTTP/"):
            raise RuntimeError(f"unexpected TLS response: {response[:80]!r}")
        status = response.split(b"\r\n", 1)[0].decode("ascii")
        print(f"PYTHON WASI TLS ROUNDTRIP: {status}")
    finally:
        sock.close()


class Run(exports.Run):
    def run(self) -> None:
        if len(sys.argv) == 4 and sys.argv[0] == "tls-probe":
            tls_probe(sys.argv[1], int(sys.argv[2]), sys.argv[3])
            return
        if len(sys.argv) != 8 or sys.argv[0] != "postgres":
            raise RuntimeError(
                "expected postgres HOST PORT USER PASSWORD DATABASE MESSAGE TLS_NAME"
            )
        roundtrip(
            sys.argv[1],
            int(sys.argv[2]),
            sys.argv[3],
            sys.argv[4],
            sys.argv[5],
            sys.argv[6],
            sys.argv[7],
        )
