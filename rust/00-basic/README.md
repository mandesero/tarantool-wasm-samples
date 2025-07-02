# Rust hello world

The smallest Rust `wasi:cli/run` component.

Complete the [root setup](https://github.com/mandesero/tarantool-wasm-samples), then build and run from the repository root:

```sh
make build SAMPLE=rust/00-basic
make run SAMPLE=rust/00-basic
```

Expected result: `Hello from Rust WASM!`. Generated bindings, `.tarawasm/`, and `dist/adder.wasm` are build artifacts and are intentionally ignored.
