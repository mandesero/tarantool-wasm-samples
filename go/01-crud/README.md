## JS Example: Basic test

### How to run

```bash
tarawasm build
tarantool run.lua
```

---

### Expected output

```
2025-07-03 12:17:09.508 [17659] main/104/run.lua/run run.lua:19 I> Load WASM module...
2025-07-03 12:17:09.611 [17659] main/104/run.lua/run run.lua:21 I> Run WASM module...
2025-07-03 12:17:09.614 [17659] unknown main.go:125 I> {{{}} 512}
2025-07-03 12:17:09.614 [17659] unknown main.go:132 I> [0]
2025-07-03 12:17:09.614 [17659] unknown main.go:132 I> [1]
2025-07-03 12:17:09.614 [17659] unknown main.go:132 I> [2]
2025-07-03 12:17:09.614 [17659] unknown main.go:132 I> [3]
2025-07-03 12:17:09.614 [17659] unknown main.go:132 I> [4]
2025-07-03 12:17:09.614 [17659] main/117/main main.go:104 I> [0]
2025-07-03 12:17:09.614 [17659] main/117/main main.go:104 I> [1]
2025-07-03 12:17:09.614 [17659] main/117/main main.go:104 I> [2]
2025-07-03 12:17:09.614 [17659] main/117/main main.go:104 I> [3]
2025-07-03 12:17:09.614 [17659] main/117/main main.go:104 I> [4]
2025-07-03 12:17:09.615 [17659] unknown main.go:143 I> {{{}} 0 512 0}
2025-07-03 12:17:09.615 [17659] unknown main.go:163 I> From iter [0]
2025-07-03 12:17:09.615 [17659] unknown main.go:163 I> From iter [1]
2025-07-03 12:17:09.615 [17659] unknown main.go:163 I> From iter [2]
2025-07-03 12:17:09.615 [17659] unknown main.go:163 I> From iter [3]
2025-07-03 12:17:09.615 [17659] unknown main.go:163 I> From iter [4]
2025-07-03 12:17:09.615 [17659] main/104/run.lua/run run.lua:24 I> WASM module finished...
```
