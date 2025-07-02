#!/bin/sh
set -eu

script_dir=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
repo_dir=$(dirname -- "$script_dir")
tarantool_bin=${TARANTOOL:-tarantool}
component="$repo_dir/python/11-websocket/dist/adder.wasm"

[ -f "$component" ] || {
    echo "SKIP WebSocket integration: missing $component; run make build SAMPLE=python/11-websocket" >&2
    exit 0
}

work_dir=$(mktemp -d)
websocket_port=$(python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1]); s.close()')
message="websocket message $$"
output="$work_dir/output.log"
cleanup() {
    rm -rf -- "$work_dir"
}
trap cleanup EXIT HUP INT TERM

(
    cd "$work_dir"
    timeout 60 env \
        TARANTOOL_CPATH="$repo_dir/.rocks/lib/tarantool/?.so;;" \
        WEBSOCKET_PORT="$websocket_port" \
        WEBSOCKET_MESSAGE="$message" \
        "$tarantool_bin" "$repo_dir/python/11-websocket/run.lua"
) >"$output" 2>&1 || {
    cat "$output"
    exit 1
}
grep -F "PYTHON WEBSOCKET ROUNDTRIP: echo:$message" "$output" >/dev/null || {
    cat "$output"
    echo "missing websockets success marker" >&2
    exit 1
}
cat "$output"

if ss -ltn "sport = :$websocket_port" | grep -q LISTEN; then
    echo "WebSocket test port $websocket_port was left listening" >&2
    exit 1
fi
cleanup
trap - EXIT HUP INT TERM
echo "WEBSOCKET INTEGRATION PASSED on released port $websocket_port"
