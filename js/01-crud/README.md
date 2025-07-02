# JavaScript CRUD

Looks up a Tarantool space and index, then inserts and updates a tuple through the current `0.1.4` WIT API.

Complete the [root setup](https://github.com/mandesero/tarantool-wasm-samples), then build and run from the repository root:

```sh
make build SAMPLE=js/01-crud
make run SAMPLE=js/01-crud
```

Expected result: `JS | Update successful`. Generated bindings, `.tarawasm/`, and `dist/adder.wasm` are build artifacts and are intentionally ignored.
