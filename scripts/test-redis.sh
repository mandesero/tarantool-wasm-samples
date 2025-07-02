#!/bin/sh
set -eu

script_dir=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
repo_dir=$(dirname -- "$script_dir")
tarantool_bin=${TARANTOOL:-tarantool}
redis_image=${REDIS_IMAGE:-redis:8.10.0-alpine}
component="$repo_dir/python/09-redis/dist/adder.wasm"

command -v docker >/dev/null 2>&1 || {
    echo "SKIP Redis integration: Docker is not installed" >&2
    exit 0
}
docker info >/dev/null 2>&1 || {
    echo "SKIP Redis integration: Docker daemon is unavailable" >&2
    exit 0
}
docker image inspect "$redis_image" >/dev/null 2>&1 || {
    echo "SKIP Redis integration: missing $redis_image; run make redis-image" >&2
    exit 0
}
[ -f "$component" ] || {
    echo "SKIP Redis integration: missing $component; run make build SAMPLE=python/09-redis" >&2
    exit 0
}

work_dir=$(mktemp -d)
container_name="tarantool-wasm-redis-$$"
redis_port=$(python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1]); s.close()')
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
    -p "127.0.0.1:$redis_port:6379" \
    "$redis_image" \
    redis-server --save '' --appendonly no >/dev/null

ready=false
attempt=0
while [ "$attempt" -lt 30 ]; do
    if docker exec "$container_name" redis-cli ping 2>/dev/null | grep -Fx PONG >/dev/null; then
        ready=true
        break
    fi
    attempt=$((attempt + 1))
    sleep 1
done
if [ "$ready" = false ]; then
    docker logs "$container_name" >&2
    echo "Redis readiness timeout" >&2
    exit 1
fi

key="tarawasm:test:$$"
channel="tarawasm-events-$$"
message="redis message $$"
output="$work_dir/output.log"
(
    cd "$work_dir"
    timeout 60 env \
        TARANTOOL_CPATH="$repo_dir/.rocks/lib/tarantool/?.so;;" \
        REDIS_PORT="$redis_port" \
        REDIS_KEY="$key" \
        REDIS_CHANNEL="$channel" \
        REDIS_MESSAGE="$message" \
        "$tarantool_bin" "$repo_dir/python/09-redis/run.lua"
) >"$output" 2>&1 || {
    cat "$output"
    exit 1
}
grep -F "PYTHON REDIS ROUNDTRIP: value=$message pubsub=$message" "$output" >/dev/null || {
    cat "$output"
    echo "missing redis-py success marker" >&2
    exit 1
}
cat "$output"

cleanup
trap - EXIT HUP INT TERM
if docker ps -a --format '{{.Names}}' | grep -Fx "$container_name" >/dev/null; then
    echo "Redis test container was left behind" >&2
    exit 1
fi
if ss -ltn "sport = :$redis_port" | grep -q LISTEN; then
    echo "Redis test port $redis_port was left listening" >&2
    exit 1
fi
echo "REDIS INTEGRATION PASSED on released port $redis_port"
