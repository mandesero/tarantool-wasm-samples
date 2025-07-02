#!/bin/sh
set -eu

script_dir=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
repo_dir=$(dirname -- "$script_dir")
tarantool_bin=${TARANTOOL:-tarantool}
nats_image=${NATS_IMAGE:-nats:2.14.4-alpine}
component="$repo_dir/python/10-nats/dist/adder.wasm"

command -v docker >/dev/null 2>&1 || {
    echo "SKIP NATS integration: Docker is not installed" >&2
    exit 0
}
docker info >/dev/null 2>&1 || {
    echo "SKIP NATS integration: Docker daemon is unavailable" >&2
    exit 0
}
docker image inspect "$nats_image" >/dev/null 2>&1 || {
    echo "SKIP NATS integration: missing $nats_image; run make nats-image" >&2
    exit 0
}
[ -f "$component" ] || {
    echo "SKIP NATS integration: missing $component; run make build SAMPLE=python/10-nats" >&2
    exit 0
}

work_dir=$(mktemp -d)
container_name="tarantool-wasm-nats-$$"
nats_port=$(python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1]); s.close()')
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
    -p "127.0.0.1:$nats_port:4222" \
    "$nats_image" -p 4222 >/dev/null

ready=false
attempt=0
while [ "$attempt" -lt 30 ]; do
    if python3 -c \
        'import socket, sys; socket.create_connection(("127.0.0.1", int(sys.argv[1])), 0.2).close()' \
        "$nats_port" >/dev/null 2>&1; then
        ready=true
        break
    fi
    attempt=$((attempt + 1))
    sleep 1
done
if [ "$ready" = false ]; then
    docker logs "$container_name" >&2
    echo "NATS readiness timeout" >&2
    exit 1
fi

subject="tarawasm.events.$$"
request_subject="tarawasm.echo.$$"
message="nats message $$"
output="$work_dir/output.log"
(
    cd "$work_dir"
    timeout 60 env \
        TARANTOOL_CPATH="$repo_dir/.rocks/lib/tarantool/?.so;;" \
        NATS_PORT="$nats_port" \
        NATS_SUBJECT="$subject" \
        NATS_REQUEST_SUBJECT="$request_subject" \
        NATS_MESSAGE="$message" \
        "$tarantool_bin" "$repo_dir/python/10-nats/run.lua"
) >"$output" 2>&1 || {
    cat "$output"
    exit 1
}
grep -F "PYTHON NATS ROUNDTRIP: pubsub=$message request=reply:$message" "$output" >/dev/null || {
    cat "$output"
    echo "missing nats-py success marker" >&2
    exit 1
}
cat "$output"

cleanup
trap - EXIT HUP INT TERM
if docker ps -a --format '{{.Names}}' | grep -Fx "$container_name" >/dev/null; then
    echo "NATS test container was left behind" >&2
    exit 1
fi
if ss -ltn "sport = :$nats_port" | grep -q LISTEN; then
    echo "NATS test port $nats_port was left listening" >&2
    exit 1
fi
echo "NATS INTEGRATION PASSED on released port $nats_port"
