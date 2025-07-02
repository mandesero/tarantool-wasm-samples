#!/bin/sh
set -eu

script_dir=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
repo_dir=$(dirname -- "$script_dir")
tarantool_bin=$(printenv TARANTOOL 2>/dev/null || printf '%s' tarantool)

resolve_ipv4() {
    if command -v getent >/dev/null 2>&1; then
        getent ahostsv4 "$1" | awk 'NR == 1 { print $1 }'
    elif command -v python3 >/dev/null 2>&1; then
        python3 -c 'import socket,sys; print(socket.gethostbyname(sys.argv[1]))' "$1"
    else
        return 1
    fi
}

server_name=$(printenv TLS_PROBE_SERVER_NAME 2>/dev/null || printf '%s' example.com)
ip=$(printenv TLS_PROBE_IP 2>/dev/null || true)
if [ -z "$ip" ]; then
    ip=$(resolve_ipv4 "$server_name" || true)
fi
[ -n "$ip" ] || {
    echo "SKIP Python TLS smoke: cannot resolve $server_name to IPv4" >&2
    exit 0
}

output=$(
    TARANTOOL_CPATH="$repo_dir/.rocks/lib/tarantool/?.so;;" \
    TLS_PROBE_IP="$ip" TLS_PROBE_SERVER_NAME="$server_name" \
    "$tarantool_bin" "$repo_dir/python/13-postgres-tls/tls-probe.lua" 2>&1
)
printf '%s\n' "$output"
printf '%s\n' "$output" | grep -F "PYTHON WASI TLS ROUNDTRIP: HTTP/" >/dev/null
