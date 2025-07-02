#!/bin/sh
set -eu

script_dir=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
repo_dir=$(dirname -- "$script_dir")
tarantool_bin=${TARANTOOL:-tarantool}
mqtt_image=${MQTT_IMAGE:-eclipse-mosquitto:2.1.2-alpine}
component="$repo_dir/python/12-mqtt/dist/adder.wasm"

command -v docker >/dev/null 2>&1 || {
    echo "SKIP MQTT integration: Docker is not installed" >&2
    exit 0
}
docker info >/dev/null 2>&1 || {
    echo "SKIP MQTT integration: Docker daemon is unavailable" >&2
    exit 0
}
docker image inspect "$mqtt_image" >/dev/null 2>&1 || {
    echo "SKIP MQTT integration: missing $mqtt_image; run make mqtt-image" >&2
    exit 0
}
[ -f "$component" ] || {
    echo "SKIP MQTT integration: missing $component; run make build SAMPLE=python/12-mqtt" >&2
    exit 0
}

work_dir=$(mktemp -d)
container_name="tarantool-wasm-mqtt-$$"
mqtt_port=$(python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1]); s.close()')
cleaned=false
cleanup() {
    if [ "$cleaned" = false ]; then
        docker rm -f "$container_name" >/dev/null 2>&1 || true
        rm -rf -- "$work_dir"
        cleaned=true
    fi
}
trap cleanup EXIT HUP INT TERM

config="$work_dir/mosquitto.conf"
printf '%s\n' \
    'listener 1883 0.0.0.0' \
    'allow_anonymous true' \
    'persistence false' \
    >"$config"

docker run -d --name "$container_name" \
    -p "127.0.0.1:$mqtt_port:1883" \
    -v "$config:/mosquitto/config/mosquitto.conf:ro" \
    "$mqtt_image" >/dev/null

ready=false
attempt=0
while [ "$attempt" -lt 30 ]; do
    if python3 -c \
        'import socket, sys; socket.create_connection(("127.0.0.1", int(sys.argv[1])), 0.2).close()' \
        "$mqtt_port" >/dev/null 2>&1; then
        ready=true
        break
    fi
    attempt=$((attempt + 1))
    sleep 1
done
if [ "$ready" = false ]; then
    docker logs "$container_name" >&2
    echo "MQTT readiness timeout" >&2
    exit 1
fi

topic="tarawasm/events/$$"
message="mqtt message $$"
output="$work_dir/output.log"
(
    cd "$work_dir"
    timeout 60 env \
        TARANTOOL_CPATH="$repo_dir/.rocks/lib/tarantool/?.so;;" \
        MQTT_PORT="$mqtt_port" \
        MQTT_TOPIC="$topic" \
        MQTT_MESSAGE="$message" \
        "$tarantool_bin" "$repo_dir/python/12-mqtt/run.lua"
) >"$output" 2>&1 || {
    cat "$output"
    exit 1
}
grep -F "PYTHON PAHO MQTT ROUNDTRIP: $message" "$output" >/dev/null || {
    cat "$output"
    echo "missing Paho MQTT success marker" >&2
    exit 1
}
cat "$output"

cleanup
trap - EXIT HUP INT TERM
if docker ps -a --format '{{.Names}}' | grep -Fx "$container_name" >/dev/null; then
    echo "MQTT test container was left behind" >&2
    exit 1
fi
if ss -ltn "sport = :$mqtt_port" | grep -q LISTEN; then
    echo "MQTT test port $mqtt_port was left listening" >&2
    exit 1
fi
echo "MQTT INTEGRATION PASSED on released port $mqtt_port"
