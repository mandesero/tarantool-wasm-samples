# Go hello world

The smallest Go `wasi:cli/run` component.

Complete the [root setup](https://github.com/mandesero/tarantool-wasm-samples), then build and run from the repository root:

```sh
make build SAMPLE=go/00-basic
make run SAMPLE=go/00-basic
```

Expected result: `Hello from Go WASM!`. Generated bindings, `.tarawasm/`, and `dist/adder.wasm` are build artifacts and are intentionally ignored.
