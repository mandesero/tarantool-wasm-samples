## Python Example: WebServer Flask Test

### Docker Note (Flask dependency)

If you build inside Docker, **Flask must be available in the container**.

To add Flask to the Docker image:

```bash
git clone https://github.com/mandesero/tarawasm.git
cd tarawasm
echo "flask" >> requirements.txt
docker build -t mandeser0/tarawasm .
```

After rebuild, the Dockerized build and runtime will have Flask preinstalled.

---

### How to run

```bash
tarawasm build
tarantool run.lua
```

---

### Expected output

**Tarantool log:**

```
2025-07-02 16:48:43.731 [211058] main/104/run.lua/run run.lua:19 I> Load WASM module...
2025-07-02 16:48:45.453 [211058] main/104/run.lua/run run.lua:21 I> Run WASM module...
 * Serving Flask app 'main'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:36847
Press CTRL+C to quit
```

**HTTP requests from another terminal:**

```bash
$ curl http://127.0.0.1:36847/insert/test_space/4,d
{"message":"Inserted, tuple_ptr = 74275a007894"}

$ curl http://127.0.0.1:36847/insert/test_space/5,a
{"message":"Inserted, tuple_ptr = 74275a0078cc"}

$ curl http://127.0.0.1:36847/content/test_space
{"space":"test_space","tuples":[[4,"d"],[5,"a"]]}

$ curl http://127.0.0.1:36847/time
{"time":"2025-07-02 13:49:25"}
```

**More Tarantool logs:**

```
127.0.0.1 - - [02/Jul/2025 13:48:58] "GET /insert/ts/4,d HTTP/1.1" 400 -
2025-07-02 16:49:04.599 [211058] unknown main.py:88 I> PY | Try to insert [4, 'd'] to space Space(id=512)
127.0.0.1 - - [02/Jul/2025 13:49:04] "GET /insert/test_space/4,d HTTP/1.1" 200 -
2025-07-02 16:49:08.742 [211058] unknown main.py:88 I> PY | Try to insert [5, 'a'] to space Space(id=512)
127.0.0.1 - - [02/Jul/2025 13:49:08] "GET /insert/test_space/5,a HTTP/1.1" 200 -
2025-07-02 16:49:15.645 [211058] unknown main.py:103 I> PY | Get space content - space 'test_space'
127.0.0.1 - - [02/Jul/2025 13:49:15] "GET /content/test_space HTTP/1.1" 200 -
127.0.0.1 - - [02/Jul/2025 13:49:25] "GET /time HTTP/1.1" 200 -
^C
2025-07-02 16:49:30.420 [211058] main/104/run.lua/run run.lua:24 I> WASM module finished...
```
