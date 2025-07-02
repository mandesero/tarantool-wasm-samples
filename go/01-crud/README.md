# Go CRUD

Runs a Tarantool transaction and inserts tuples through the current `0.1.4` WIT API.

Complete the [root setup](https://github.com/mandesero/tarantool-wasm-samples), then build and run from the repository root:

```sh
make build SAMPLE=go/01-crud
make run SAMPLE=go/01-crud
```

Expected result: `[4]`. Generated bindings, `.tarawasm/`, and `dist/adder.wasm` are build artifacts and are intentionally ignored.
