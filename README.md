# 🧩 Working with Tarantool WASM Examples

## Prerequisites

1. **Place your `wasm.so` file** in the root of your project.

2. **Install CLI tooling** for working with WASM components:
   👉 [https://github.com/mandesero/tarawasm](https://github.com/mandesero/tarawasm)

   You can use the provided Docker image:

   ```bash
   docker pull mandeser0/tarawasm:latest
   alias tarawasm='docker run --rm -v "$PWD":/work -w /work mandeser0/tarawasm'
   ```

3. **Choose an example:**

   ```bash
   cd python/00-basic

   # Generate language bindings if needed
   tarawasm bind

   # Build the WASM component
   tarawasm build

   # Run the component in Tarantool
   tarantool run.lua
   ```

---

## 🛠️ Building Tarantool with WASM support

Before you can run WASM components, you need a special Tarantool build with `TARANTOOL_WASM=ON`.

```bash
git clone https://github.com/mandesero/tarantool
cd tarantool
git checkout wasm

mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Debug -DENABLE_BACKTRACE=ON -DTARANTOOL_WASM=ON
make -j
```

After building, **ensure `tarantool` from `build/src/tarantool` is used** when running examples.

---

## 🔧 Using `tarawasm` CLI

### Overview

[`tarawasm`](https://github.com/mandesero/tarawasm) is a CLI tool for initializing, binding, and building WASM components in Python, Rust, Go, JS, and other languages.

---

### 🐍 Python Example

```bash
mkdir my-component && cd my-component
cp <some-path>/docs:adder@0.1.0.wasm .

# Initialize Python project
tarawasm init --lang python --wasm-file docs:adder@0.1.0.wasm adder

# Generate WIT bindings
tarawasm bind

# 📝 Now you can write your own code in `main.py`

# Build component
tarawasm build

# 🔗 Make sure to place your `wasm.so` in this directory as well.

# Run with tarantool
tarantool run.lua ./adder.wasm
```

---

## Running WASM Component in Tarantool

### Example `run.lua`:

```lua
-- run.lua
local wasm = require('wasm')
local wasm_module_path = ...

log.info("Load WASM module...")
local module = wasm.load(wasm_module_path)

log.info("Run WASM module...")
local handle = wasm.run(module)

wasm.join(handle)
log.info("WASM module finished...")
```

### Run it:

```bash
tarantool run.lua ./my_component.wasm
```
