## Python Example: Box tuple Test

### How to run

```bash
tarawasm build
tarantool run.lua
```

---

### Expected output

```
2025-07-02 15:24:42.001 [168803] main/104/run.lua/run run.lua:19 I> Load WASM module...
2025-07-02 15:24:43.697 [168803] main/104/run.lua/run run.lua:21 I> Run WASM module...
2025-07-02 15:24:43.703 [168803] unknown say.rs:25 I> PY | ===== Test box tuple start =====
2025-07-02 15:24:43.705 [168803] unknown say.rs:25 I> PY | Default format (ptr): 0x573fadbec6e0
2025-07-02 15:24:43.705 [168803] unknown say.rs:25 I> PY | Created tuple [1, 'abc', {'x': 42}], ptr=0x75425c8300e0
2025-07-02 15:24:43.705 [168803] unknown say.rs:25 I> PY | tuple.ref() => 0
2025-07-02 15:24:43.705 [168803] unknown say.rs:25 I> PY | field_count = 3
2025-07-02 15:24:43.705 [168803] unknown say.rs:25 I> PY | bsize = 10
2025-07-02 15:24:43.705 [168803] unknown say.rs:25 I> PY | to_buf (decoded) = [1, 'abc', {'x': 42}]
2025-07-02 15:24:43.705 [168803] unknown say.rs:25 I> PY | format (ptr) = 0x573fadbec6e0
2025-07-02 15:24:43.705 [168803] unknown say.rs:25 I> PY | field[0] = 1
2025-07-02 15:24:43.706 [168803] unknown say.rs:25 I> PY | field[1] = abc
2025-07-02 15:24:43.706 [168803] unknown say.rs:25 I> PY | field[2] = {'x': 42}
2025-07-02 15:24:43.706 [168803] unknown say.rs:25 I> PY | field_by_path "[3].x" = 42
2025-07-02 15:24:43.706 [168803] unknown say.rs:25 I> PY | updated tuple (set field 1 to 'xyz') = ['xyz', 'abc', {'x': 42}]
2025-07-02 15:24:43.706 [168803] unknown say.rs:25 I> PY | upserted tuple (increment field 1 by 100) = [101, 'abc', {'x': 42}]
2025-07-02 15:24:43.706 [168803] unknown say.rs:25 I> PY | validate = True
2025-07-02 15:24:43.706 [168803] unknown say.rs:25 I> PY | Created key_def: 128925993000496
2025-07-02 15:24:43.707 [168803] unknown say.rs:25 I> PY | compare(tup, other) = 0
2025-07-02 15:24:43.707 [168803] unknown say.rs:25 I> PY | compare_with_key(tup, [1]) = 0
2025-07-02 15:24:43.707 [168803] unknown say.rs:25 I> PY | tuple.unref() done
2025-07-02 15:24:43.707 [168803] unknown say.rs:25 I> PY | ===== Test box tuple done =====
2025-07-02 15:24:43.707 [168803] unknown say.rs:25 I> PY | ===== Test box tuple iterator start =====
2025-07-02 15:24:43.707 [168803] unknown say.rs:25 I> PY | Created tuple [1, 'abc', {'x': 42}], ptr=0x75425c8300e0
2025-07-02 15:24:43.707 [168803] unknown say.rs:25 I> PY | Created tuple iterator
2025-07-02 15:24:43.707 [168803] unknown say.rs:25 I> PY | Iterator pos=1: 1
2025-07-02 15:24:43.707 [168803] unknown say.rs:25 I> PY | Iterator pos=2: abc
2025-07-02 15:24:43.707 [168803] unknown say.rs:25 I> PY | Iterator pos=3: {'x': 42}
2025-07-02 15:24:43.707 [168803] unknown say.rs:25 I> PY | Position after iteration: 3
2025-07-02 15:24:43.707 [168803] unknown say.rs:25 I> PY | Rewound iterator
2025-07-02 15:24:43.707 [168803] unknown say.rs:25 I> PY | After rewind, next field (pos=1): 1
2025-07-02 15:24:43.707 [168803] unknown say.rs:25 I> PY | After seek(1), pos=2
2025-07-02 15:24:43.707 [168803] unknown say.rs:25 I> PY | Field after seek: {'x': 42}
2025-07-02 15:24:43.707 [168803] unknown say.rs:25 I> PY | ===== Test box tuple iterator done =====
2025-07-02 15:24:43.708 [168803] main/104/run.lua/run run.lua:24 I> WASM module finished...
```
