# Python TCP client/server

This logical sample has two WIT-first build units and one Lua lifecycle host. Complete the [root setup](https://github.com/mandesero/tarantool-wasm-samples), then run:

```sh
make build SAMPLE=python/02-network/01-python-network/server
make build SAMPLE=python/02-network/01-python-network/client
SAMPLE_PORT=18081 make run SAMPLE=python/02-network/01-python-network
```

The host starts the server, polls readiness without a fixed sleep, runs the client, joins both handles, drops both modules, and verifies an echo plus graceful guest shutdown. Omit `SAMPLE_PORT` to use 65432; the smoke suite allocates a free port.
