# Kafka with aiokafka

Uses the ready-made `aiokafka` client inside a Python WASI component. The guest
starts an `AIOKafkaProducer`, publishes one UTF-8 message, stops the producer,
then starts an `AIOKafkaConsumer` and verifies the same value and offset.

Complete the [root setup](https://github.com/mandesero/tarantool-wasm-samples),
then run the fully automated local integration test:

```sh
make kafka-image
make build SAMPLE=python/07-kafka
make kafka-smoke
```

The test starts a pinned single-node Redpanda broker on a free loopback port,
creates a unique topic, runs the component through Tarantool, and removes the
container. Expected output includes:

```text
PYTHON AIOKAFKA ROUNDTRIP: aiokafka message ...
KAFKA INTEGRATION PASSED on released port ...
```

To use an already running plaintext Kafka-compatible broker, first create the
topic and ensure its advertised listener resolves to loopback, then run:

```sh
KAFKA_PORT=9092 \
KAFKA_TOPIC=tarawasm-python \
KAFKA_MESSAGE='hello from Python WASM' \
make run SAMPLE=python/07-kafka
```

`aiokafka` and its transitive packages are pinned in `requirements.txt` and are
installed by `make deps`. Producer and consumer `stop()` calls are protected by
`finally`, and the read has a ten-second timeout. The runtime network policy is
limited to `127.0.0.1`, but not to one port: Python's asyncio event loop needs an
additional ephemeral loopback socket pair. This sample intentionally does not
cover TLS, SASL, consumer groups, or production broker configuration.

A Go equivalent is intentionally not included. Both `segmentio/kafka-go`
`v0.4.51` and the older `v0.2.3` fail to compile with the TinyGo toolchain in
the current tarawasm image because TinyGo lacks required `net`, `crypto/tls`,
DNS resolver, and `pprof` APIs. No library fork or handwritten protocol is
hidden in this sample.
