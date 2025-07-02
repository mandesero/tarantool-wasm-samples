# Python hello world

The smallest Python `wasi:cli/run` component.

Complete the [root setup](https://github.com/mandesero/tarantool-wasm-samples), then build and run from the repository root:

```sh
make build SAMPLE=python/00-basic
make run SAMPLE=python/00-basic
```

Expected result: `Hello from Python WASM!`. Generated bindings, `.tarawasm/`, and `dist/adder.wasm` are build artifacts and are intentionally ignored.
