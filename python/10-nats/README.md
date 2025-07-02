# NATS with nats-py

Uses the ready-made official `nats-py` asyncio client. The guest performs a
publish/subscribe roundtrip followed by request/reply, then unsubscribes and
drains the connection deterministically.

Complete the [root setup](https://github.com/mandesero/tarantool-wasm-samples),
then run the automated local integration test:

```sh
make nats-image
make build SAMPLE=python/10-nats
make nats-smoke
```

The test starts pinned NATS Server 2.14.4 on a free loopback port, waits for the
TCP listener, runs the component, and removes the container. Expected output:

```text
PYTHON NATS ROUNDTRIP: pubsub=nats message ... request=reply:nats message ...
NATS INTEGRATION PASSED on released port ...
```

To use an existing plaintext NATS server reachable at loopback:

```sh
NATS_PORT=4222 \
NATS_SUBJECT=tarawasm.events \
NATS_REQUEST_SUBJECT=tarawasm.echo \
NATS_MESSAGE='hello from Python WASM' \
make run SAMPLE=python/10-nats
```

`nats-py` is pinned in `requirements.txt`. Connect, flush, message, and drain
operations have finite timeouts, and all subscriptions and the client are
closed on error paths. Current componentize Python lacks the `ssl` module, so
`ssl_compat.py` exposes only the names that nats-py imports; attempting to create
a TLS context fails explicitly. This sample therefore accepts only plaintext
`nats://` loopback endpoints and must not be pointed at an untrusted network.
