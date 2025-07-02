local wasm = require('wasm')
local log = require('log')

log.info("Load WASM module...")
local module = wasm.load("./adder.wasm")
log.info("Run WASM module...")
local handle = wasm.run(module)
wasm.join(handle)
log.info("WASM module finished...")
