# Tarantool WASM samples

This repository contains small, reproducible WebAssembly Component Model guests for the current `tarantool-wasm` Lua runtime. WIT is the source of truth; `tarawasm` generates bindings and produces every final component at `dist/adder.wasm`. Generated bindings, build intermediates, native modules, database files, and final components are not committed.

## Compatibility and prerequisites

The verified setup is Linux x86-64, Tarantool 3.7.0, Rust 1.94.0 for runtime builds, Docker, GNU Make, and `mandeser0/tarawasm:latest`. The optional integrations use pinned Redpanda `v25.1.3`, PostgreSQL `17.6-alpine`, Redis `8.10.0-alpine`, NATS `2.14.4-alpine`, and Eclipse Mosquitto `2.1.2-alpine` as local test services. The upstream runtime release matrix also covers Fedora 39, CentOS 8, RED OS 7.3.4, and Astra Linux 1.7 on x86-64. Native `wasm.so` files are platform-, architecture-, libc-, and Tarantool-version dependent; do not copy an arbitrary artifact between platforms.

Pull the exact image used by this workflow:

```sh
make tarawasm-image
make kafka-image    # pull the optional pinned Kafka test broker
make postgres-image # pull the optional pinned PostgreSQL test server
make redis-image    # pull the optional pinned Redis test server
make nats-image     # pull the optional pinned NATS test server
make mqtt-image     # pull the optional pinned MQTT test broker
```

No host installation of tarawasm is needed. Every build runs the latest image with the repository mounted at `/work`.

## Obtain and connect `wasm.so`

If a compatible module is already built, pass its explicit absolute path to the safe local helper:

```sh
make setup WASM_SO=/absolute/path/to/libtarantool_wasm_rs.so
```

The helper verifies that the source is a regular file and creates only `.rocks/lib/tarantool/wasm.so`. It is idempotent for the same target and refuses to replace any different file or symlink. It never modifies a system installation.

The run workflow sets the loader path as follows:

```sh
export TARANTOOL_CPATH="$PWD/.rocks/lib/tarantool/?.so;;"
tarantool -e "local wasm = require('wasm'); assert(type(wasm.load) == 'function'); print('require wasm: ok')"
```

For an application that configures Lua directly, the equivalent is:

```lua
package.cpath = '/absolute/path/to/tarantool-wasm-samples/.rocks/lib/tarantool/?.so;' .. package.cpath
local wasm = require('wasm')
```

To build the module from source using the current upstream instructions:

```sh
git clone --recursive https://github.com/tarantool/tarantool-wasm-rs.git
cd tarantool-wasm-rs
cargo install just
just install-wkg
just
# Debug artifact:
# target/debug/libtarantool_wasm_rs.so

just build-release
# Release artifact:
# target/x86_64-unknown-linux-gnu/release/libtarantool_wasm_rs.so
```

Then return here and run `make setup` with the absolute debug or release artifact path. Copying instead of linking is also safe if done explicitly: create `.rocks/lib/tarantool`, verify that `wasm.so` does not already exist, then copy the chosen artifact there.

## Quickstart

Python hello-world is the shortest sample:

```sh
make tarawasm-image
make setup WASM_SO=/absolute/path/to/libtarantool_wasm_rs.so
make build SAMPLE=python/00-basic
make run SAMPLE=python/00-basic
```

Expected output:

```text
Hello from Python WASM!
```

All `run.lua` files resolve paths relative to themselves, so the command works from any current directory through `make run`.

## Repository layout

Each build unit follows the same convention:

```text
sample/
├── wit/                 handwritten contract; deps points to root wit-deps
├── main.* or src/       handwritten guest source
├── tarawasm.json        current WIT-first build configuration
├── run.lua              Tarantool host and lifecycle
├── generated bindings  ignored (wit_world/, internal/, src/bindings.rs)
├── .tarawasm/           ignored intermediates
└── dist/adder.wasm      ignored final component
```

`wit-deps/` contains pinned WIT package components plus `SHA256SUMS`. The HTTP callback interface is the runtime-local experimental `docs:adder/lua-callback@0.1.3`; it is deliberately copied as local handwritten WIT because it is not yet a stable published `tarantool:tarantool` dependency.

## Samples

All worlds are named `adder` and export `wasi:cli/run`. Build one with `make build SAMPLE=<path>` and run it with `make run SAMPLE=<path>`.

| Sample path | Guest | Idea / API | Execution model |
| --- | --- | --- | --- |
| `python/00-basic` | Python | hello world | `wasm.run`, join, drop |
| `js/00-basic` | JavaScript | hello world | `wasm.run`, join, drop |
| `go/00-basic` | Go | hello world | `wasm.run`, join, drop |
| `rust/00-basic` | Rust | hello world | `wasm.run`, join, drop |
| `js/01-crud` | JavaScript | space insert/update | `wasm.run` on TX, join, drop |
| `go/01-crud` | Go | transaction and tuple insertion | `wasm.run` on TX, join, drop |
| `rust/01-crud` | Rust | space insert/update | `wasm.run` on TX, join, drop |
| `python/01-tarantool/00-box` | Python | space/index CRUD and index resource | `wasm.run` on TX |
| `python/01-tarantool/01-tuple` | Python | tuple and iterator resource | `wasm.run` on TX |
| `python/01-tarantool/02-error` | Python | current error API | `wasm.run` |
| `python/01-tarantool/03-key-def` | Python | key definitions | `wasm.run` |
| `python/01-tarantool/04-sequence` | Python | sequences | `wasm.run` on TX |
| `python/01-tarantool/05-tuple-format` | Python | tuple formats | `wasm.run` |
| `python/02-network/00-wasi-network` | Python | raw WASI TCP resources | local echo + `wasm.run` |
| `go/02-wasi-network` | Go | raw WASI TCP resources | local echo + `wasm.run` |
| `python/02-network/01-python-network` | Python | standard-library TCP | server/client run, join, drop |
| `python/03-webserver-flask` | Python | HTTP server calling dynamic Lua handlers | callback resource + `wasm.run/cancel` |
| `python/04-grpc` | Python | local gRPC server/client | run, join client, cancel server |
| `python/05-async` | Python | asyncio scheduling | `wasm.run`, join, drop |
| `python/06-cli` | Python | interactive Python console | inherited stdin + `wasm.run` |
| `python/07-kafka` | Python | `aiokafka` producer/consumer roundtrip | asyncio + `wasm.run`, join, drop |
| `python/08-postgres` | Python | `pg8000` transaction roundtrip | DB-API + `wasm.run`, join, drop |
| `python/09-redis` | Python | `redis-py` pipeline and Pub/Sub roundtrip | asyncio + `wasm.run`, join, drop |
| `python/10-nats` | Python | `nats-py` Pub/Sub and request/reply | asyncio + `wasm.run`, drain, drop |
| `python/11-websocket` | Python | `websockets` local server/client roundtrip | asyncio + `wasm.run`, close, drop |
| `python/12-mqtt` | Python | Eclipse Paho MQTT QoS 1 roundtrip | manual Paho loop + `wasm.run`, disconnect, drop |
| `python/13-postgres-tls` | Python | `pg8000` over host-side WASI TLS | DB-API + `wasm.run`, join, drop |

The exact per-unit command behind `make build SAMPLE=python/00-basic` is:

```sh
docker run --rm -v "$PWD:/work" -w /work/python/00-basic \
  mandeser0/tarawasm:latest all
```

## Build, test, and clean

```sh
make deps       # verify WIT hashes and install pinned Python packages locally
make build      # build all 29 guest components
make lint       # diff, JSON, and available shell checks
make smoke      # execute all logical samples with the real wasm.so
make kafka-smoke # run aiokafka against an isolated local broker
make postgres-smoke # run pg8000 against isolated PostgreSQL
make postgres-tls-smoke # validate host-side WASI TLS with a public certificate
make redis-smoke # run redis-py against isolated Redis
make nats-smoke # run nats-py against isolated NATS
make websocket-smoke # run local websockets server/client roundtrip
make mqtt-smoke # run Paho MQTT against isolated Mosquitto
make test       # lint + build + smoke + service integrations when their images are installed
make clean      # tarawasm clean; removes generated artifacts only
```

Network examples accept `SAMPLE_PORT`; the smoke suite allocates free loopback ports. Every background example waits for readiness, consumes each join/cancel handle exactly once, drops every module, and checks that no sample process or listening port remains.

## Troubleshooting

- `module 'wasm' not found`: run `make setup` and verify `.rocks/lib/tarantool/wasm.so`; do not rely on the current directory.
- `undefined symbol`, loader failure, or platform mismatch: rebuild `wasm.so` for the installed Tarantool, CPU, libc, and supported Linux target.
- Wrong `package.cpath`: preserve the default tail with `;;` in `TARANTOOL_CPATH`, or prepend the absolute `.rocks/lib/tarantool/?.so` path in Lua.
- “core module instead of component”: build with `tarawasm ... all`; do not pass an intermediate core `.wasm` file to `wasm.load`.
- Missing WIT dependency: run `make deps`; verify `wit-deps/SHA256SUMS` and the sample's `wit/deps` link.
- tarawasm schema or CLI mismatch: pull `mandeser0/tarawasm:latest`; legacy `--wasm-file` configs are not supported here.
- Occupied port: set a free value, for example `SAMPLE_PORT=18080 make run SAMPLE=python/03-webserver-flask`.
- `callback ... is not registered`: register the exact `http-handler` name; after unregister the HTTP sample intentionally returns 503 rather than crashing.
- Missing Tarantool: install compatible Tarantool 3.7.0. Missing `luatest` is reported as a skip only by tests that specifically require it; the repository smoke suite itself uses Tarantool directly.
- Build works but gRPC imports fail: run `make deps`; packages are pinned in `python/04-grpc/requirements.txt` and installed under ignored `.tarawasm/site-packages`.
- Kafka integration is skipped: run `make kafka-image`, build `python/07-kafka`, and retry `make kafka-smoke`. For an external broker, its advertised listener must resolve to the allowed loopback address and port.
- PostgreSQL integration is skipped: run `make postgres-image`, build `python/08-postgres`, and retry `make postgres-smoke`. This baseline sample uses a plaintext loopback endpoint.
- PostgreSQL TLS smoke fails: build `python/13-postgres-tls`, confirm outbound TCP/443 and DNS, or override both `TLS_PROBE_IP` and `TLS_PROBE_SERVER_NAME`.
- Python package imports ssl: componentize Python still lacks general _ssl. The PostgreSQL sample has a narrow synchronous wasi:tls adapter; asyncio clients need separate transport integration.
- Redis integration is skipped: run `make redis-image`, build `python/09-redis`, and retry `make redis-smoke`. External servers must be plaintext loopback endpoints because componentize Python currently has no `ssl` module.
- NATS integration is skipped: run `make nats-image`, build `python/10-nats`, and retry `make nats-smoke`. External servers must be plaintext loopback endpoints because componentize Python currently has no `ssl` module.
- WebSocket integration is skipped: build `python/11-websocket` and retry `make websocket-smoke`. Set `WEBSOCKET_PORT` to a free loopback port for a direct run.
- MQTT integration is skipped: run `make mqtt-image`, build `python/12-mqtt`, and retry `make mqtt-smoke`. External brokers must be plaintext loopback endpoints because componentize Python currently has no `ssl` module.
