## Python Example: Box error Test

### How to run

```bash
tarawasm build
tarantool run.lua
```

---

### Expected output

```
2025-07-02 15:26:51.906 [169840] main/104/run.lua/run run.lua:19 I> Load WASM module...
2025-07-02 15:26:53.604 [169840] main/104/run.lua/run run.lua:21 I> Run WASM module...
2025-07-02 15:26:53.611 [169840] unknown say.rs:25 I> PY | ===== Test box error start =====
2025-07-02 15:26:53.613 [169840] unknown main.py:29 I> PY | Running test_error
2025-07-02 15:26:53.613 [169840] unknown say.rs:25 I> PY | No existing error found
2025-07-02 15:26:53.613 [169840] unknown say.rs:25 I> PY | Created error: [228] from python: Test (at /0/main.py:40)
2025-07-02 15:26:53.613 [169840] unknown say.rs:25 I> PY | Error set
2025-07-02 15:26:53.613 [169840] unknown say.rs:25 I> PY | Error after set: [228] ClientError: Test (at /0/main.py:40)
2025-07-02 15:26:53.613 [169840] unknown say.rs:25 I> PY | No existing error found
2025-07-02 15:26:53.613 [169840] unknown say.rs:25 I> PY | ===== Test box error done =====
2025-07-02 15:26:53.614 [169840] main/104/run.lua/run run.lua:24 I> WASM module finished...
```
