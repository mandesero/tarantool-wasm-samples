# Go raw WASI networking

Uses generated WASI socket, stream, poll, and network resources against a local configurable echo server.

Complete the [root setup](https://github.com/mandesero/tarantool-wasm-samples), then build and run from the repository root:

```sh
make build SAMPLE=go/02-wasi-network
make run SAMPLE=go/02-wasi-network
```

Expected result: `RAW GO WASI NETWORK PASSED`. Generated bindings, `.tarawasm/`, and `dist/adder.wasm` are build artifacts and are intentionally ignored.
