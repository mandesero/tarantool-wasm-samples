## Python Example: Box API Test

### How to run

```bash
tarawasm build
tarantool run.lua
```

---

### Expected output

```
2025-07-02 15:01:21.368 [159012] main/104/run.lua/run run.lua:19 I> Load WASM module...
2025-07-02 15:01:23.094 [159012] main/104/run.lua/run run.lua:21 I> Run WASM module...
2025-07-02 15:01:23.101 [159012] unknown say.rs:25 I> PY | ===== Test box API start =====
2025-07-02 15:01:23.103 [159012] unknown say.rs:25 I> PY | Schema version: 85
2025-07-02 15:01:23.103 [159012] unknown say.rs:25 I> PY | Space: id=512
2025-07-02 15:01:23.103 [159012] unknown say.rs:25 I> PY | Index: space_id=512, id=0, index_base=0
2025-07-02 15:01:23.104 [159012] unknown say.rs:25 I> PY | Inserted: [1, 'Alice', 25], tuple_ptr=0x7af3b1007894, decoded=[1, 'Alice', 25]
2025-07-02 15:01:23.104 [159012] unknown say.rs:25 I> PY | Inserted: [2, 'Bob', 30], tuple_ptr=0x7af3b10078cc, decoded=[2, 'Bob', 30]
2025-07-02 15:01:23.104 [159012] main/117/main say.rs:25 I> PY | Inserted: [3, 'Charlie', 35], tuple_ptr=0x7af3b1007904, decoded=[3, 'Charlie', 35]
2025-07-02 15:01:23.104 [159012] main/117/main say.rs:25 I> PY | Inserted: [4, 'David', 40], tuple_ptr=0x7af3b100793c, decoded=[4, 'David', 40]
2025-07-02 15:01:23.104 [159012] main/117/main say.rs:25 I> PY | Inserted: [5, 'Eve', 4], tuple_ptr=0x7af3b1007974, decoded=[5, 'Eve', 4]
2025-07-02 15:01:23.105 [159012] unknown say.rs:25 I> PY | Updated id=1 (age=26), tuple_ptr=0x7af3b10079ac, decoded=[1, 'Alice', 26]
2025-07-02 15:01:23.105 [159012] unknown say.rs:25 I> PY | Replaced id=2 -> ['Bob Jr.', 31], tuple_ptr=0x7af3b1007894, decoded=[2, 'Bob Jr.', 31]
2025-07-02 15:01:23.105 [159012] unknown say.rs:25 I> PY | Upserted id=6 (inserted new)
2025-07-02 15:01:23.105 [159012] unknown say.rs:25 I> PY | Upserted id=1 (age incremented)
2025-07-02 15:01:23.105 [159012] unknown say.rs:25 I> PY | Deleted id=3, tuple_ptr=0x7af3b1007904, decoded=[3, 'Charlie', 35]
2025-07-02 15:01:23.105 [159012] unknown say.rs:25 I> PY | Iterating over space content:
2025-07-02 15:01:23.106 [159012] unknown say.rs:25 I> PY |	Tuple: [1, 'Alice', 27]
2025-07-02 15:01:23.106 [159012] unknown say.rs:25 I> PY |	Tuple: [2, 'Bob Jr.', 31]
2025-07-02 15:01:23.106 [159012] unknown say.rs:25 I> PY |	Tuple: [4, 'David', 40]
2025-07-02 15:01:23.106 [159012] unknown say.rs:25 I> PY |	Tuple: [5, 'Eve', 4]
2025-07-02 15:01:23.106 [159012] unknown say.rs:25 I> PY |	Tuple: [6, 'Frank', 50]
2025-07-02 15:01:23.106 [159012] unknown say.rs:25 I> PY | Truncated space
2025-07-02 15:01:23.106 [159012] unknown say.rs:25 I> PY | ===== Test box API done =====
2025-07-02 15:01:23.107 [159012] main/104/run.lua/run run.lua:24 I> WASM module finished...
```
