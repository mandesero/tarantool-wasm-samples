## Python Example: Box sequence Test

### How to run

```bash
tarawasm build
tarantool run.lua
```

---

### Expected output

```
2025-07-02 15:33:14.585 [172660] main/104/run.lua/run run.lua:21 I> Load WASM module...
2025-07-02 15:33:16.279 [172660] main/104/run.lua/run run.lua:23 I> Run WASM module...
2025-07-02 15:33:16.285 [172660] unknown say.rs:25 I> PY | ===== Test box sequence start =====
2025-07-02 15:33:16.287 [172660] unknown say.rs:25 I> PY | sequence.current error: BoxError(message="Sequence 'id_seq' is not started", type='ClientError', code=212, payload=None, file='./src/box/sequence.c', line=438)
2025-07-02 15:33:16.287 [172660] unknown say.rs:25 I> PY | sequence.next: 1000
2025-07-02 15:33:16.287 [172660] unknown say.rs:25 I> PY | sequence.current: 1000
2025-07-02 15:33:16.288 [172660] unknown say.rs:25 I> PY | sequence.set: 42
2025-07-02 15:33:16.288 [172660] unknown say.rs:25 I> PY | sequence.current: 42
2025-07-02 15:33:16.288 [172660] unknown say.rs:25 I> PY | sequence.reset: done
2025-07-02 15:33:16.288 [172660] unknown say.rs:25 I> PY | sequence.current after reset error: BoxError(message="Sequence 'id_seq' is not started", type='ClientError', code=212, payload=None, file='./src/box/sequence.c', line=438)
2025-07-02 15:33:16.288 [172660] unknown say.rs:25 I> PY | ===== Test box sequence done =====
2025-07-02 15:33:16.288 [172660] main/104/run.lua/run run.lua:26 I> WASM module finished...
```
