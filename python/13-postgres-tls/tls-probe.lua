local source = assert(debug.getinfo(1, 'S').source)
local script = assert(source:match('^@(.+)$'), 'tls-probe.lua must be loaded from a file')
local dir = assert(script:match('^(.*[/\\])'), 'tls-probe.lua has no directory')
local runner = dofile(dir .. '../../lua/sample.lua')

local ip = assert(os.getenv('TLS_PROBE_IP'), 'TLS_PROBE_IP is required')
local port = tonumber(os.getenv('TLS_PROBE_PORT')) or 443
local server_name = os.getenv('TLS_PROBE_SERVER_NAME') or 'example.com'

runner.run(dir .. 'dist/adder.wasm', runner.default_options({
    args = {'tls-probe', ip, tostring(port), server_name},
    inherit_network = true,
    allowed_ips = {ip},
    allowed_ports = {port},
    memory_limit = 256 * 1024 * 1024,
    max_instructions = 4 * 1000 * 1000 * 1000,
}))
