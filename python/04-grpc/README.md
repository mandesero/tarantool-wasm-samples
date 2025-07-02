## Python Example: GRPC Client Server Test

### Docker Note (grpclib[protobuf] dependency)

If you build inside Docker, **grpclib[protobuf] must be available in the container**.

To add grpclib[protobuf] to the Docker image:

```bash
git clone https://github.com/mandesero/tarawasm.git
cd tarawasm
echo "grpclib[protobuf]" >> requirements.txt
docker build -t mandeser0/tarawasm .
```

After rebuild, the Dockerized build and runtime will have grpclib[protobuf] preinstalled.

---

### How to run [Client]

```bash
tarawasm build
python3 client/server.py > server.log 2>&1 &
tarantool run.lua ./client/adder.wasm
```

---

### Expected output

**Tarantool log:**

```
Load WASM module...
Run WASM module...
Received: Hello, Alice!
WASM module finished...
```

**On the server side:**

```bash
$ pkill python3
$ cat server.log
Serving on 127.0.0.1:50051
```

---

### How to run [Server]

```bash
tarawasm build
tarantool run.lua ./server/adder.wasm
```

---

### Expected output

**Tarantool log:**

```
Load WASM module...
Run WASM module...
Serving on 0.0.0.0:50051
```

**On the client side:**

```bash
$ python3 server/client.py
Received: Hello, Alice!
```
