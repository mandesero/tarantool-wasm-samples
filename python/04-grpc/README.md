# Python gRPC client/server

This logical sample has a gRPC server component and a client component. Complete the [root setup](https://github.com/mandesero/tarantool-wasm-samples), then run:

```sh
make deps
make build SAMPLE=python/04-grpc/server
make build SAMPLE=python/04-grpc/client
SAMPLE_PORT=18082 make run SAMPLE=python/04-grpc
```

Dependencies and transitive versions are pinned in `requirements.txt` and installed only under ignored `.tarawasm/site-packages`. The Lua host waits for readiness, joins the client, cancels the long-running server, and drops both modules. Asyncio needs unrestricted loopback networking because its internal socket pair uses an ephemeral port. Omit `SAMPLE_PORT` to use 50051; tests allocate a free port.
