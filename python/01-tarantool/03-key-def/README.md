## Python Example: Box key-def Test

### How to run

```bash
tarawasm build
tarantool run.lua
```

---

### Expected output

```
2025-07-02 15:30:17.915 [171335] main/104/run.lua/run run.lua:19 I> Load WASM module...
2025-07-02 15:30:19.610 [171335] main/104/run.lua/run run.lua:21 I> Run WASM module...
2025-07-02 15:30:19.616 [171335] unknown say.rs:25 I> PY | ===== Test box key-def start =====
2025-07-02 15:30:19.619 [171335] unknown say.rs:25 I> PY | Created key_def: t1 = 136137041919648
2025-07-02 15:30:19.619 [171335] unknown say.rs:25 I> PY | Key parts count: t1 = 2
2025-07-02 15:30:19.619 [171335] unknown say.rs:25 I> PY | t1 dump_parts:
	KeyPart(field_no=0, field_type='unsigned', collation=None, path=None, flags=<KeyPartFlags.IS_NULLABLE: 1>)
	KeyPart(field_no=3, field_type='string', collation='unicode', path='t1', flags=<KeyPartFlags.EXCLUDE_NULL: 2>)
2025-07-02 15:30:19.619 [171335] unknown say.rs:25 I> PY | Created key_def: t2 = 136137041763824
2025-07-02 15:30:19.619 [171335] unknown say.rs:25 I> PY | Key parts count: t2 = 1
2025-07-02 15:30:19.619 [171335] unknown say.rs:25 I> PY | t2 dump_parts:
	KeyPart(field_no=1, field_type='string', collation=None, path=None, flags=<KeyPartFlags.EXCLUDE_NULL: 2>)
2025-07-02 15:30:19.619 [171335] unknown say.rs:25 I> PY | t1 duplicated: 136137041918928
2025-07-02 15:30:19.619 [171335] unknown say.rs:25 I> PY | Key parts count: t1_dup = 2
2025-07-02 15:30:19.619 [171335] unknown say.rs:25 I> PY | t1_dup dump_parts:
	KeyPart(field_no=0, field_type='unsigned', collation=None, path=None, flags=<KeyPartFlags.IS_NULLABLE: 1>)
	KeyPart(field_no=3, field_type='string', collation='unicode', path='t1', flags=<KeyPartFlags.EXCLUDE_NULL: 2>)
2025-07-02 15:30:19.619 [171335] unknown say.rs:25 I> PY | Merged t1 and t2 → merged_t = 136137041764112
2025-07-02 15:30:19.619 [171335] unknown say.rs:25 I> PY | Key parts count: merged_t = 3
2025-07-02 15:30:19.619 [171335] unknown say.rs:25 I> PY | merged_t dump_parts:
	KeyPart(field_no=0, field_type='unsigned', collation=None, path=None, flags=<KeyPartFlags.IS_NULLABLE: 1>)
	KeyPart(field_no=3, field_type='string', collation='unicode', path='t1', flags=<KeyPartFlags.EXCLUDE_NULL: 2>)
	KeyPart(field_no=1, field_type='string', collation=None, path=None, flags=<KeyPartFlags.EXCLUDE_NULL: 2>)
2025-07-02 15:30:19.620 [171335] unknown say.rs:25 I> PY | validate_key(valid_key): True, size = 6
2025-07-02 15:30:19.620 [171335] unknown say.rs:25 I> PY | validate_full_key(valid_key): True, size = 6
2025-07-02 15:30:19.620 [171335] unknown say.rs:25 E> PY | validate_key(invalid_key) error: BoxError(message='Supplied key type of part 0 does not match index part type: expected unsigned', type='ClientError', code=18, payload=None, file='./src/box/key_def.h', line=878)
2025-07-02 15:30:19.620 [171335] unknown say.rs:25 I> PY | Deleted all key_defs
2025-07-02 15:30:19.620 [171335] unknown say.rs:25 I> PY | ===== Test box key-def done =====
2025-07-02 15:30:19.620 [171335] main/104/run.lua/run run.lua:24 I> WASM module finished...
```
