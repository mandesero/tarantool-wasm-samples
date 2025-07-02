#!/bin/sh
set -eu

script_dir=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
repo_dir=$(dirname -- "$script_dir")
tarantool_bin=${TARANTOOL:-tarantool}
kafka_image=${KAFKA_IMAGE:-docker.redpanda.com/redpandadata/redpanda:v25.1.3}
component="$repo_dir/python/07-kafka/dist/adder.wasm"

command -v docker >/dev/null 2>&1 || {
    echo "SKIP Kafka integration: Docker is not installed" >&2
    exit 0
}
docker info >/dev/null 2>&1 || {
    echo "SKIP Kafka integration: Docker daemon is unavailable" >&2
    exit 0
}
docker image inspect "$kafka_image" >/dev/null 2>&1 || {
    echo "SKIP Kafka integration: missing $kafka_image; run make kafka-image" >&2
    exit 0
}
[ -f "$component" ] || {
    echo "SKIP Kafka integration: missing $component; run make build SAMPLE=python/07-kafka" >&2
    exit 0
}

work_dir=$(mktemp -d)
container_name="tarantool-wasm-kafka-$$"
kafka_port=$(python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1]); s.close()')
cleaned=false
cleanup() {
    if [ "$cleaned" = false ]; then
        docker rm -f "$container_name" >/dev/null 2>&1 || true
        rm -rf -- "$work_dir"
        cleaned=true
    fi
}
trap cleanup EXIT HUP INT TERM

docker run -d --name "$container_name" \
    -p "127.0.0.1:$kafka_port:19092" \
    "$kafka_image" \
    redpanda start \
    --overprovisioned --smp 1 --memory 512M --reserve-memory 0M \
    --node-id 0 --check=false \
    --kafka-addr 'internal://0.0.0.0:9092,external://0.0.0.0:19092' \
    --advertise-kafka-addr "internal://127.0.0.1:9092,external://127.0.0.1:$kafka_port" \
    >/dev/null

ready=false
attempt=0
while [ "$attempt" -lt 30 ]; do
    if docker exec "$container_name" rpk cluster health --exit-when-healthy >/dev/null 2>&1; then
        ready=true
        break
    fi
    attempt=$((attempt + 1))
    sleep 1
done
if [ "$ready" = false ]; then
    docker logs "$container_name" >&2
    echo "Kafka broker readiness timeout" >&2
    exit 1
fi

topic="tarawasm-python-$$"
message="aiokafka message $$"
docker exec "$container_name" rpk topic create "$topic" >/dev/null
output="$work_dir/output.log"
(
    cd "$work_dir"
    timeout 60 env \
        TARANTOOL_CPATH="$repo_dir/.rocks/lib/tarantool/?.so;;" \
        KAFKA_PORT="$kafka_port" KAFKA_TOPIC="$topic" KAFKA_MESSAGE="$message" \
        "$tarantool_bin" "$repo_dir/python/07-kafka/run.lua"
) >"$output" 2>&1 || {
    cat "$output"
    exit 1
}
grep -F "PYTHON AIOKAFKA ROUNDTRIP: $message" "$output" >/dev/null || {
    cat "$output"
    echo "missing aiokafka success marker" >&2
    exit 1
}
cat "$output"

cleanup
trap - EXIT HUP INT TERM
if docker ps -a --format '{{.Names}}' | grep -Fx "$container_name" >/dev/null; then
    echo "Kafka test container was left behind" >&2
    exit 1
fi
if ss -ltn "sport = :$kafka_port" | grep -q LISTEN; then
    echo "Kafka test port $kafka_port was left listening" >&2
    exit 1
fi
echo "KAFKA INTEGRATION PASSED on released port $kafka_port"
