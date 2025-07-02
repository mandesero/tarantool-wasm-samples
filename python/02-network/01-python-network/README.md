## Python Example: Client Server Test

### How to run

```bash
tarawasm build
tarantool run.lua
```

---

### Expected output

```
Load WASM modules...
Run WASM modules...
Connected to 127.0.0.1:65432
Sending: b'Hello, server!'
Connected by ('127.0.0.1', 39602)
Received: b'Hello, server!'
Sending: b'Another message'
Received: b'Another message'
WASM module finished...
```
