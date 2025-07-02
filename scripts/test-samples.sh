#!/bin/sh
set -eu

script_dir=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
repo_dir=$(dirname -- "$script_dir")
tarantool_bin=${TARANTOOL:-tarantool}
command -v "$tarantool_bin" >/dev/null 2>&1 || {
    echo "SKIP smoke: Tarantool is not installed: $tarantool_bin" >&2
    exit 0
}
[ -f "$repo_dir/.rocks/lib/tarantool/wasm.so" ] || {
    echo "SKIP smoke: run make setup WASM_SO=/absolute/path/to/wasm.so" >&2
    exit 0
}

work_dir=$(mktemp -d)
ports=""
cleanup() {
    rm -rf "$work_dir"
}
trap cleanup EXIT HUP INT TERM

free_port() {
    python3 -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1]); s.close()'
}

run_sample() {
    sample=$1
    expected=$2
    shift 2
    sample_name=$(printf '%s' "$sample" | tr '/' '_')
    output="$work_dir/$sample_name.log"
    sample_work="$work_dir/work_$sample_name"
    mkdir "$sample_work"
    echo "==> smoke $sample"
    (
        cd "$sample_work"
        if [ -n "${SAMPLE_INPUT:-}" ]; then
            printf '%b' "$SAMPLE_INPUT" |
                timeout 180 env TARANTOOL_CPATH="$repo_dir/.rocks/lib/tarantool/?.so;;" \
                    "$@" "$tarantool_bin" "$repo_dir/$sample/run.lua"
        else
            timeout 180 env TARANTOOL_CPATH="$repo_dir/.rocks/lib/tarantool/?.so;;" \
                "$@" "$tarantool_bin" "$repo_dir/$sample/run.lua"
        fi
    ) >"$output" 2>&1 || {
        cat "$output"
        return 1
    }
    if ! grep -F "$expected" "$output" >/dev/null; then
        cat "$output"
        echo "missing success marker: $expected" >&2
        return 1
    fi
}

run_sample python/00-basic 'Hello from Python WASM!'
run_sample js/00-basic 'Hello from JS WASM!'
run_sample go/00-basic 'Hello from Go WASM!'
run_sample rust/00-basic 'Hello from Rust WASM!'
run_sample js/01-crud 'JS | Update successful'
run_sample go/01-crud '[4]'
run_sample rust/01-crud 'RUST | Update successful'
run_sample python/01-tarantool/00-box 'Test box API done'
run_sample python/01-tarantool/01-tuple 'Test box tuple iterator done'
run_sample python/01-tarantool/02-error 'Test box error done'
run_sample python/01-tarantool/03-key-def 'Test box key-def done'
run_sample python/01-tarantool/04-sequence 'Test box sequence done'
run_sample python/01-tarantool/05-tuple-format 'Test box tuple format done'
run_sample python/05-async 'Task 2 completed after 1 second'
SAMPLE_INPUT='print("CLI SMOKE:", 1 + 2)\nlog.write(LogLevel.INFO, "CLI LOG SMOKE", None)\n' \
    run_sample python/06-cli 'CLI SMOKE: 3'

port=$(free_port); ports="$ports $port"
run_sample python/02-network/00-wasi-network 'RAW PYTHON WASI NETWORK PASSED' SAMPLE_PORT="$port"
port=$(free_port); ports="$ports $port"
run_sample go/02-wasi-network 'RAW GO WASI NETWORK PASSED' SAMPLE_PORT="$port"
port=$(free_port); ports="$ports $port"
run_sample python/02-network/01-python-network 'TCP LIFECYCLE PASSED' SAMPLE_PORT="$port"
port=$(free_port); ports="$ports $port"
run_sample python/04-grpc 'GRPC LIFECYCLE PASSED' SAMPLE_PORT="$port"
port=$(free_port); ports="$ports $port"
run_sample python/03-webserver-flask 'HTTP CALLBACK DEMO PASSED' SAMPLE_PORT="$port"

if pgrep -af "tarantool.*$repo_dir/.*/run.lua" >/dev/null; then
    echo "sample Tarantool process was left running" >&2
    pgrep -af "tarantool.*$repo_dir/.*/run.lua" >&2
    exit 1
fi
for port in $ports; do
    if ss -ltn "sport = :$port" | grep -q LISTEN; then
        echo "sample port $port was left listening" >&2
        exit 1
    fi
done

echo "all sample smoke tests passed"
