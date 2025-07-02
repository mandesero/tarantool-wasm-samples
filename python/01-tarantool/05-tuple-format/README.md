## Python Example: Box tuple format Test

### How to run

```bash
tarawasm build
tarantool run.lua
```

---

### Expected output

```
2025-07-02 15:35:15.886 [173637] main/104/run.lua/run run.lua:19 I> Load WASM module...
2025-07-02 15:35:17.576 [173637] main/104/run.lua/run run.lua:21 I> Run WASM module...
2025-07-02 15:35:17.582 [173637] unknown say.rs:25 I> PY | ===== Test box API start =====
2025-07-02 15:35:17.585 [173637] unknown say.rs:25 I> PY | Created key_def: 132855015816896
2025-07-02 15:35:17.585 [173637] unknown say.rs:25 I> PY | Created tuple_format: 132855015816448
2025-07-02 15:35:17.585 [173637] unknown say.rs:25 I> PY | Called tuple_format.ref
2025-07-02 15:35:17.585 [173637] unknown say.rs:25 I> PY | Called tuple_format.unref
2025-07-02 15:35:17.585 [173637] unknown say.rs:25 I> PY | Default tuple_format: 101958228764432
2025-07-02 15:35:17.585 [173637] unknown say.rs:25 I> PY | ===== Test box API done =====
2025-07-02 15:35:17.585 [173637] main/104/run.lua/run run.lua:24 I> WASM module finished...
```
