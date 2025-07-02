from wit_world import exports
from wit_world.imports import lua_callback, msgpack

import importlib.metadata
import io
import json
import socket
import sys

# componentize-py exposes the imported WIT zlib interface as __zlib.
import __zlib
sys.modules["zlib"] = __zlib
importlib.metadata.version = lambda _: ""
"".encode("idna")

from flask import Flask, Response, request

app = Flask(__name__)
handler = None
stopping = False


def encode(value) -> bytes:
    return msgpack.encode(json.dumps(value).encode("utf-8"))


def decode(payload: bytes):
    return json.loads(msgpack.decode(payload).decode("utf-8"))


@app.post("/__shutdown")
def shutdown():
    global stopping
    stopping = True
    return Response("stopping\n", content_type="text/plain; charset=utf-8")


@app.route("/", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE"])
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def dispatch(path: str):
    try:
        result = decode(handler.call(encode({
            "method": request.method,
            "path": "/" + path,
            "body": request.get_data(as_text=True),
        })))
        return Response(
            str(result.get("body", "")),
            status=int(result.get("status", 200)),
            headers=result.get("headers") or {},
            content_type="text/plain; charset=utf-8",
        )
    except Exception as exc:
        return Response(
            f"callback unavailable: {exc}\n",
            status=503,
            content_type="text/plain; charset=utf-8",
        )


def invoke_flask(method: str, path: str, body: bytes, port: int):
    captured = {}

    def start_response(status, headers, exc_info=None):
        captured["status"] = status
        captured["headers"] = headers

    environ = {
        "REQUEST_METHOD": method,
        "SCRIPT_NAME": "",
        "PATH_INFO": path,
        "QUERY_STRING": "",
        "SERVER_NAME": "127.0.0.1",
        "SERVER_PORT": str(port),
        "SERVER_PROTOCOL": "HTTP/1.1",
        "REMOTE_ADDR": "127.0.0.1",
        "CONTENT_LENGTH": str(len(body)),
        "wsgi.version": (1, 0),
        "wsgi.url_scheme": "http",
        "wsgi.input": io.BytesIO(body),
        "wsgi.errors": sys.stderr,
        "wsgi.multithread": False,
        "wsgi.multiprocess": False,
        "wsgi.run_once": False,
    }
    iterable = app(environ, start_response)
    try:
        payload = b"".join(iterable)
    finally:
        close = getattr(iterable, "close", None)
        if close is not None:
            close()
    return captured["status"], captured["headers"], payload


def send_response(conn, status: str, headers, body: bytes) -> None:
    values = [(name, value) for name, value in headers if name.lower() != "connection"]
    values.append(("Connection", "close"))
    values.append(("Content-Length", str(len(body))))
    head = [f"HTTP/1.0 {status}"] + [f"{name}: {value}" for name, value in values]
    conn.sendall(("\r\n".join(head) + "\r\n\r\n").encode("latin-1") + body)


def serve(port: int) -> None:
    global handler, stopping
    stopping = False
    # The resource is acquired before Lua registers the named closure.
    with lua_callback.open("http-handler") as acquired:
        handler = acquired
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(("127.0.0.1", port))
            server.listen(8)
            print(f"FLASK READY http://127.0.0.1:{port}", flush=True)
            while not stopping:
                conn, _ = server.accept()
                with conn:
                    raw = conn.recv(16 * 1024)
                    if not raw:
                        continue
                    line = raw.split(b"\r\n", 1)[0].decode("ascii")
                    method, path, _ = line.split(" ", 2)
                    body = raw.split(b"\r\n\r\n", 1)[1]
                    status, headers, payload = invoke_flask(method, path, body, port)
                    send_response(conn, status, headers, payload)


class Run(exports.Run):
    def run(self) -> None:
        serve(int(sys.argv[0]) if sys.argv else 8080)
