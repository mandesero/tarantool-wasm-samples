## Go Example: Wasi Network Test

### How to run

```bash
tarawasm build
python3 server.py > server.log 2>&1 &
tarantool run.lua
```

---

### Expected output

```
Load WASM module...
Run WASM module...
Msg from server: Hello from server!

WASM module finished...
```

### Server logs

```
$ cat server.log

Server listening on 127.0.0.1:12121
Connection established with ('127.0.0.1', 40900)
Received from ('127.0.0.1', 40900): hello from go wasm

Connection closed by ('127.0.0.1', 40900)
```
