#!/bin/sh
set -eu

script_dir=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
repo_dir=$(dirname -- "$script_dir")
command_name=${1:-}
[ -n "$command_name" ] || { echo "usage: $0 COMMAND [ARG ...]" >&2; exit 2; }
shift

case "$command_name" in
link-wasm)
    [ "$#" -eq 1 ] || { echo "usage: $0 link-wasm /absolute/path/to/wasm.so" >&2; exit 2; }
    source_path=$1
    case "$source_path" in
        /*) ;;
        *) echo "wasm.so source path must be absolute: $source_path" >&2; exit 2 ;;
    esac
    [ -f "$source_path" ] || { echo "not a regular file: $source_path" >&2; exit 2; }
    loader_dir="$repo_dir/.rocks/lib/tarantool"
    destination="$loader_dir/wasm.so"
    mkdir -p "$loader_dir"
    if [ -L "$destination" ]; then
        current_target=$(readlink "$destination")
        [ "$current_target" = "$source_path" ] && {
            echo "wasm.so is already linked to $source_path"
            exit 0
        }
        echo "refusing to replace symlink: $destination -> $current_target" >&2
        exit 1
    fi
    if [ -e "$destination" ]; then
        cmp -s "$source_path" "$destination" && {
            echo "wasm.so already has identical contents: $destination"
            exit 0
        }
        echo "refusing to replace existing file: $destination" >&2
        exit 1
    fi
    ln -s "$source_path" "$destination"
    echo "linked $destination -> $source_path"
    ;;
check-wasm)
    module="$repo_dir/.rocks/lib/tarantool/wasm.so"
    [ -f "$module" ] || {
        echo "missing $module; run make setup WASM_SO=/absolute/path/to/wasm.so" >&2
        exit 2
    }
    tarantool_bin=${TARANTOOL:-tarantool}
    TARANTOOL_CPATH="$repo_dir/.rocks/lib/tarantool/?.so;;" "$tarantool_bin" -e "local wasm=require('wasm'); assert(type(wasm.load)=='function'); print('require wasm: ok'); os.exit(0)"
    ;;
tarawasm)
    [ "$#" -ge 1 ] || { echo "tarawasm arguments are required" >&2; exit 2; }
    image=${TARAWASM_IMAGE:-mandeser0/tarawasm:latest}
    docker image inspect "$image" >/dev/null 2>&1 || {
        echo "missing image $image; run make tarawasm-image" >&2
        exit 2
    }
    find "$repo_dir" -name tarawasm.json -print | LC_ALL=C sort |
    while IFS= read -r config; do
        component_dir=$(dirname "$config")
        relative=${component_dir#"$repo_dir"/}
        echo "==> $relative: tarawasm $*"
        docker run --rm -v "$repo_dir:/work" -w "/work/$relative" "$image" "$@"
    done
    ;;
tarawasm-one)
    [ "$#" -ge 2 ] || { echo "usage: $0 tarawasm-one SAMPLE COMMAND [ARG ...]" >&2; exit 2; }
    sample=$1
    shift
    sample_dir=$(CDPATH='' cd -- "$repo_dir/$sample" && pwd)
    case "$sample_dir/" in
        "$repo_dir"/*/) ;;
        *) echo "sample escapes repository: $sample" >&2; exit 2 ;;
    esac
    [ -f "$sample_dir/tarawasm.json" ] || { echo "missing tarawasm.json: $sample" >&2; exit 2; }
    image=${TARAWASM_IMAGE:-mandeser0/tarawasm:latest}
    relative=${sample_dir#"$repo_dir"/}
    docker run --rm -v "$repo_dir:/work" -w "/work/$relative" "$image" "$@"
    ;;
deps)
    (cd "$repo_dir" && sha256sum -c wit-deps/SHA256SUMS)
    image=${TARAWASM_IMAGE:-mandeser0/tarawasm:latest}
    docker run --rm -v "$repo_dir:/work" -w /work "$image" \
        pip install --upgrade --only-binary=:all: -r python/04-grpc/requirements.txt
    docker run --rm -v "$repo_dir:/work" -w /work "$image" \
        pip install --upgrade --only-binary=:all: -r python/03-webserver-flask/requirements.txt
    docker run --rm -v "$repo_dir:/work" -w /work "$image" \
        pip install --upgrade --only-binary=:all: -r python/07-kafka/requirements.txt
    docker run --rm -v "$repo_dir:/work" -w /work "$image" \
        pip install --upgrade --only-binary=:all: -r python/08-postgres/requirements.txt
    docker run --rm -v "$repo_dir:/work" -w /work "$image" \
        pip install --upgrade --only-binary=:all: -r python/09-redis/requirements.txt
    docker run --rm -v "$repo_dir:/work" -w /work "$image" \
        pip install --upgrade --only-binary=:all: -r python/10-nats/requirements.txt
    docker run --rm -v "$repo_dir:/work" -w /work "$image" \
        pip install --upgrade --only-binary=:all: -r python/11-websocket/requirements.txt
    docker run --rm -v "$repo_dir:/work" -w /work "$image" \
        pip install --upgrade --only-binary=:all: -r python/12-mqtt/requirements.txt
    ;;
run)
    [ "$#" -ge 1 ] || { echo "usage: $0 run SAMPLE [ARG ...]" >&2; exit 2; }
    sample=$1
    shift
    case "$sample" in
        /*) sample_dir=$sample ;;
        *) sample_dir="$repo_dir/$sample" ;;
    esac
    sample_dir=$(CDPATH='' cd -- "$sample_dir" && pwd)
    tarantool_bin=${TARANTOOL:-tarantool}
    TARANTOOL_CPATH="$repo_dir/.rocks/lib/tarantool/?.so;;" "$tarantool_bin" "$sample_dir/run.lua" "$@"
    ;;
lint)
    git -C "$repo_dir" diff --check
    find "$repo_dir" -name tarawasm.json -print | while IFS= read -r file; do
        python3 -m json.tool "$file" >/dev/null
    done
    for script in "$repo_dir"/scripts/*.sh; do
        sh -n "$script"
    done
    if command -v shellcheck >/dev/null 2>&1; then
        shellcheck "$repo_dir"/scripts/*.sh
    else
        echo "SKIP shellcheck: shellcheck is not installed"
    fi
    ;;
smoke)
    TARANTOOL=${TARANTOOL:-tarantool} "$repo_dir/scripts/test-samples.sh"
    ;;
*)
    echo "unknown command: $command_name" >&2
    exit 2
    ;;
esac
