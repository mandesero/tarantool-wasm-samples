# Redis with redis-py

Uses the official ready-made `redis-py` client through its asyncio API. The
guest executes a transactional pipeline, verifies the stored value, subscribes
to a channel, publishes a message, receives it, and closes both Pub/Sub and the
client deterministically.

Complete the [root setup](https://github.com/mandesero/tarantool-wasm-samples),
then run the automated local integration test:

```sh
make redis-image
make build SAMPLE=python/09-redis
make redis-smoke
```

The test starts pinned Redis 8.10.0 on a free loopback port, waits for `PONG`,
runs the component, and removes the container. Expected output:

```text
PYTHON REDIS ROUNDTRIP: value=redis message ... pubsub=redis message ...
REDIS INTEGRATION PASSED on released port ...
```

To use an existing plaintext Redis server reachable at loopback:

```sh
REDIS_PORT=6379 \
REDIS_KEY=tarawasm:demo \
REDIS_CHANNEL=tarawasm-events \
REDIS_MESSAGE='hello from Python WASM' \
make run SAMPLE=python/09-redis
```

`redis-py` is pinned in `requirements.txt`. The client has finite connect and
command timeouts, and the Pub/Sub receive is bounded by an asyncio timeout.
Current componentize Python lacks the `ssl` module, so this sample uses a
plaintext loopback endpoint and must not be pointed at an untrusted network.
The example deletes its key and closes Pub/Sub and the connection pool even
when an operation fails.
