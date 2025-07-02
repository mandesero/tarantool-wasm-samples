## Python Example: CLI Test

### How to run

```bash
tarawasm build
tarantool run.lua
```

---

### Expected output

```
Load WASM module...
Run WASM module...
Python 3.12.1 (118e9d8:118e9d8, Jun 23 2025, 15:33:09) [Clang 18.1.0rc (https://github.com/llvm/llvm-project 461274b81d8641eab64d494acc on wasi
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> print(1 + 2)
3
>>> say.say_info("From python cli", None)
From python cli
>>> exit()
WASM module finished...
```
