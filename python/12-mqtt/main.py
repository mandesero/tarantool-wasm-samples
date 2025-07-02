from wit_world import exports

import sys
import time

import paho.mqtt.client as mqtt

from ssl_compat import install

install(mqtt)

"".encode("idna")


def roundtrip(port: int, topic: str, text: str) -> None:
    state = {
        "error": None,
        "publish_info": None,
        "received": None,
    }

    def on_connect(client, _userdata, _flags, reason_code, _properties) -> None:
        if reason_code.is_failure:
            state["error"] = f"MQTT connection rejected: {reason_code}"
            return
        result, _message_id = client.subscribe(topic, qos=1)
        if result != mqtt.MQTT_ERR_SUCCESS:
            state["error"] = f"MQTT subscribe failed: {result}"

    def on_subscribe(
        client,
        _userdata,
        _message_id,
        reason_codes,
        _properties,
    ) -> None:
        if not reason_codes or any(code.is_failure for code in reason_codes):
            state["error"] = f"MQTT subscription rejected: {reason_codes}"
            return
        publish_info = client.publish(topic, text.encode("utf-8"), qos=1)
        if publish_info.rc != mqtt.MQTT_ERR_SUCCESS:
            state["error"] = f"MQTT publish failed: {publish_info.rc}"
            return
        state["publish_info"] = publish_info

    def on_message(_client, _userdata, message) -> None:
        try:
            state["received"] = message.payload.decode("utf-8")
        except UnicodeDecodeError as error:
            state["error"] = f"MQTT payload is not UTF-8: {error}"

    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=f"tarawasm-{port}",
        protocol=mqtt.MQTTv5,
    )
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.connect_timeout = 5

    try:
        result = client.connect("127.0.0.1", port, keepalive=10)
        if result != mqtt.MQTT_ERR_SUCCESS:
            raise RuntimeError(f"MQTT connect failed: {result}")

        deadline = time.monotonic() + 15
        while True:
            result = client.loop(timeout=0.1)
            if result != mqtt.MQTT_ERR_SUCCESS:
                raise RuntimeError(f"MQTT network loop failed: {result}")
            if state["error"] is not None:
                raise RuntimeError(state["error"])
            publish_info = state["publish_info"]
            if state["received"] is not None and publish_info is not None:
                if publish_info.is_published():
                    break
            if time.monotonic() >= deadline:
                raise TimeoutError("MQTT roundtrip timeout")

        received = state["received"]
        if received != text:
            raise RuntimeError(f"MQTT roundtrip mismatch: {received!r}")

        result = client.disconnect()
        if result != mqtt.MQTT_ERR_SUCCESS:
            raise RuntimeError(f"MQTT disconnect failed: {result}")
        deadline = time.monotonic() + 5
        while client.is_connected() and time.monotonic() < deadline:
            result = client.loop(timeout=0.1)
            if result not in (mqtt.MQTT_ERR_SUCCESS, mqtt.MQTT_ERR_NO_CONN):
                raise RuntimeError(f"MQTT disconnect loop failed: {result}")
        if client.is_connected():
            raise TimeoutError("MQTT disconnect timeout")

        print(f"PYTHON PAHO MQTT ROUNDTRIP: {received}")
    finally:
        if client.is_connected():
            client.disconnect()
            deadline = time.monotonic() + 2
            while client.is_connected() and time.monotonic() < deadline:
                client.loop(timeout=0.05)


class Run(exports.Run):
    def run(self) -> None:
        if len(sys.argv) != 3:
            raise RuntimeError("expected arguments: PORT TOPIC MESSAGE")
        roundtrip(int(sys.argv[0]), sys.argv[1], sys.argv[2])
