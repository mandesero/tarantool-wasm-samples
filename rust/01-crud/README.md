## Rust Example: Box API Test

### Add `serde_json` to Rust dependencies

In your Rust project’s Cargo.toml, add:

```toml
[dependencies]
serde_json = "1.0"
```


### How to run

```bash
tarawasm build
tarantool run.lua
```

---

### Expected output

```
2025-07-02 17:36:31.159 [233594] main/104/run.lua/run run.lua:19 I> Load WASM module...
2025-07-02 17:36:31.177 [233594] main/104/run.lua/run run.lua:21 I> Run WASM module...
2025-07-02 17:36:31.178 [233594] unknown say.rs:25 I> RUST | Schema version: 85
2025-07-02 17:36:31.180 [233594] unknown say.rs:25 I> RUST | Space found: Space { id: 512 }
2025-07-02 17:36:31.180 [233594] unknown say.rs:25 I> RUST | Index found: Index { id: 0, space-id: 512, index-base: 0 }
2025-07-02 17:36:31.180 [233594] unknown say.rs:25 I> RUST | Insert successful, ptr = 137531379185812
2025-07-02 17:36:31.180 [233594] unknown say.rs:25 I> RUST | Decoded inserted tuple: [1,"bar"]
2025-07-02 17:36:31.180 [233594] unknown say.rs:25 I> RUST | Update successful, tuple_ptr = 137531379185868
2025-07-02 17:36:31.181 [233594] main/104/run.lua/run run.lua:24 I> WASM module finished...
```
