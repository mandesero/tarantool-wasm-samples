# MQTT with Eclipse Paho

Uses the ready-made Eclipse Paho MQTT Python client. The guest connects with
MQTT 5, subscribes to a topic at QoS 1, publishes a message at QoS 1, receives
it through the callback API, waits for the publish acknowledgement, and
disconnects cleanly.

Complete the [root setup](https://github.com/mandesero/tarantool-wasm-samples),
then run the automated local integration test:

```sh
make mqtt-image
make build SAMPLE=python/12-mqtt
make mqtt-smoke
```

The test starts pinned Eclipse Mosquitto 2.1.2 on a free loopback port, waits
for its listener, runs the component, and removes the container. Expected
output:

```text
PYTHON PAHO MQTT ROUNDTRIP: mqtt message ...
MQTT INTEGRATION PASSED on released port ...
```

To use an existing plaintext MQTT broker reachable at loopback:

```sh
MQTT_PORT=1883 \
MQTT_TOPIC=tarawasm/events \
MQTT_MESSAGE='hello from Python WASM' \
make run SAMPLE=python/12-mqtt
```

`paho-mqtt` is pinned in `requirements.txt`. The sample drives Paho's public
manual network loop instead of starting a background thread, and every wait has
a finite deadline. Current componentize Python lacks the `ssl` module;
`ssl_compat.py` supplies only the exception names Paho's plaintext socket path
needs and rejects TLS context creation explicitly. This sample supports only a
plaintext loopback broker and must not be pointed at an untrusted network.
