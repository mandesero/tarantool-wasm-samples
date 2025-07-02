# Flask server with dynamic Lua callbacks

This remains a Flask example. The Python guest owns the HTTP accept loop and invokes the Flask WSGI application for routing and request/response handling. Callback routes delegate to a Lua closure through the runtime's `handler` resource and MessagePack boundary.

Complete the [root setup](https://github.com/mandesero/tarantool-wasm-samples), then build and run the verified demonstration:

```sh
make build SAMPLE=python/03-webserver-flask
SAMPLE_PORT=18080 make run SAMPLE=python/03-webserver-flask
```

The run performs this sequence:

1. `wasm.load` receives a loopback network ACL, memory limit, fuel limit, and the configured port as a WASI argument.
2. `wasm.run` starts the guest. The guest opens and retains `lua-callback.handler("http-handler")` before any closure is registered; a pre-registration request gets a controlled 503.
3. Lua registers the first closure with `wasm.register_callback(..., {timeout_ms = 250})`; an HTTP request returns `first handler: /first`.
4. Registering the same name again replaces the closure without restarting Flask or the component; the next request returns `replacement handler: /second`.
5. `wasm.unregister_callback` removes the closure. The retained resource remains valid, and the next request receives `503 Service Unavailable` containing `is not registered` rather than crashing.
6. Lua calls the guest-owned shutdown route, consumes the background handle with `wasm.join`, then drops the module. Error paths unregister, cancel, and drop through the same cleanup routine.

Expected output includes:

```text
PRE-REGISTRATION RESPONSE: 503 Service Unavailable
FIRST RESPONSE: first handler: /first
REPLACED RESPONSE: replacement handler: /second
UNREGISTERED RESPONSE: 503 Service Unavailable
HTTP CALLBACK DEMO PASSED on port 18080
```

Flask and all transitive packages are pinned in `requirements.txt`. The request and response are Lua tables encoded by the runtime as MessagePack; no Lua function or state crosses into guest memory. `docs:adder/lua-callback@0.1.3` is a contract provided by the `tarantool-wasm-rs` library; it is not part of `tarantool-wit`. Omit `SAMPLE_PORT` to use 8080; `make smoke` chooses a free port and checks that it is released.
