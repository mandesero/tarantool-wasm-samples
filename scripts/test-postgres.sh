#!/bin/sh
set -eu

script_dir=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
repo_dir=$(dirname -- "$script_dir")
tarantool_bin=${TARANTOOL:-tarantool}
postgres_image=${POSTGRES_IMAGE:-postgres:17.6-alpine}
component="$repo_dir/python/08-postgres/dist/adder.wasm"

command -v docker >/dev/null 2>&1 || {
    echo "SKIP PostgreSQL integration: Docker is not installed" >&2
    exit 0
}
docker info >/dev/null 2>&1 || {
    echo "SKIP PostgreSQL integration: Docker daemon is unavailable" >&2
    exit 0
}
docker image inspect "$postgres_image" >/dev/null 2>&1 || {
    echo "SKIP PostgreSQL integration: missing $postgres_image; run make postgres-image" >&2
    exit 0
}
[ -f "$component" ] || {
    echo "SKIP PostgreSQL integration: missing $component; run make build SAMPLE=python/08-postgres" >&2
    exit 0
}

work_dir=$(mktemp -d)
container_name="tarantool-wasm-postgres-$$"
postgres_port=$(python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1]); s.close()')
postgres_user=tarawasm
postgres_password=tarawasm-password
postgres_database=tarawasm
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
    -e "POSTGRES_USER=$postgres_user" \
    -e "POSTGRES_PASSWORD=$postgres_password" \
    -e "POSTGRES_DB=$postgres_database" \
    -p "127.0.0.1:$postgres_port:5432" \
    "$postgres_image" >/dev/null

ready=false
attempt=0
while [ "$attempt" -lt 30 ]; do
    if docker exec "$container_name" \
        pg_isready -U "$postgres_user" -d "$postgres_database" >/dev/null 2>&1; then
        ready=true
        break
    fi
    attempt=$((attempt + 1))
    sleep 1
done
if [ "$ready" = false ]; then
    docker logs "$container_name" >&2
    echo "PostgreSQL readiness timeout" >&2
    exit 1
fi

message="pg8000 message $$"
output="$work_dir/output.log"
(
    cd "$work_dir"
    timeout 60 env \
        TARANTOOL_CPATH="$repo_dir/.rocks/lib/tarantool/?.so;;" \
        POSTGRES_PORT="$postgres_port" \
        POSTGRES_USER="$postgres_user" \
        POSTGRES_PASSWORD="$postgres_password" \
        POSTGRES_DB="$postgres_database" \
        POSTGRES_MESSAGE="$message" \
        "$tarantool_bin" "$repo_dir/python/08-postgres/run.lua"
) >"$output" 2>&1 || {
    cat "$output"
    exit 1
}
grep -F "PYTHON PG8000 ROUNDTRIP: id=1 body=$message" "$output" >/dev/null || {
    cat "$output"
    echo "missing pg8000 success marker" >&2
    exit 1
}
cat "$output"

cleanup
trap - EXIT HUP INT TERM
if docker ps -a --format '{{.Names}}' | grep -Fx "$container_name" >/dev/null; then
    echo "PostgreSQL test container was left behind" >&2
    exit 1
fi
if ss -ltn "sport = :$postgres_port" | grep -q LISTEN; then
    echo "PostgreSQL test port $postgres_port was left listening" >&2
    exit 1
fi
echo "POSTGRESQL INTEGRATION PASSED on released port $postgres_port"
