# WebSocket server and client

Uses the ready-made `websockets` asyncio library on both sides of a local
connection. The guest starts an echo server, opens a client connection, sends
a text frame, validates the response, performs the closing handshake, and
stops the listener.

Complete the [root setup](https://github.com/mandesero/tarantool-wasm-samples),
then build and run the automated integration test:

```sh
make build SAMPLE=python/11-websocket
make websocket-smoke
```

The test allocates a free loopback port and verifies that it is released after
the component exits. Expected output:

```text
PYTHON WEBSOCKET ROUNDTRIP: echo:websocket message ...
WEBSOCKET INTEGRATION PASSED on released port ...
```

To run the sample directly:

```sh
WEBSOCKET_PORT=8765 \
WEBSOCKET_MESSAGE='hello from Python WASM' \
make run SAMPLE=python/11-websocket
```

`websockets` is pinned in `requirements.txt`. Open, receive, and close
operations have finite timeouts; compression and automatic proxy discovery are
disabled for a small deterministic local example. Current componentize Python
lacks the `ssl` module, so the import-only `ssl_compat.py` rejects TLS context
creation explicitly. The sample supports only plaintext `ws://` on loopback.
