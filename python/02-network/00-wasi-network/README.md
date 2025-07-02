# Python raw WASI networking

Uses generated WASI socket, stream, poll, and network resources against a local configurable echo server.

Complete the [root setup](https://github.com/mandesero/tarantool-wasm-samples), then build and run from the repository root:

```sh
make build SAMPLE=python/02-network/00-wasi-network
make run SAMPLE=python/02-network/00-wasi-network
```

Expected result: `RAW PYTHON WASI NETWORK PASSED`. Generated bindings, `.tarawasm/`, and `dist/adder.wasm` are build artifacts and are intentionally ignored.
