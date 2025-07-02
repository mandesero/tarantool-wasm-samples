local source = assert(debug.getinfo(1, 'S').source)
local script = assert(source:match('^@(.+)$'), 'run.lua must be loaded from a file')
local dir = assert(script:match('^(.*[/\\])'), 'run.lua has no directory')
local runner = dofile(dir .. '../../lua/sample.lua')
local port = tonumber(os.getenv('WEBSOCKET_PORT')) or 8765
local message = os.getenv('WEBSOCKET_MESSAGE') or 'hello from Python WASM'

runner.run(dir .. 'dist/adder.wasm', runner.default_options({
    args = {tostring(port), message},
    inherit_network = true,
    allowed_ips = {'127.0.0.1'},
    memory_limit = 256 * 1024 * 1024,
    max_instructions = 2 * 1000 * 1000 * 1000,
}))
