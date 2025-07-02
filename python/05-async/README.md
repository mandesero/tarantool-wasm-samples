# Python asyncio

Runs two asyncio tasks and joins the component before dropping it.

Complete the [root setup](https://github.com/mandesero/tarantool-wasm-samples), then build and run from the repository root:

```sh
make build SAMPLE=python/05-async
make run SAMPLE=python/05-async
```

Expected result: `Task 2 completed after 1 second`. Generated bindings, `.tarawasm/`, and `dist/adder.wasm` are build artifacts and are intentionally ignored.
