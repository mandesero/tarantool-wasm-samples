local socket = require('socket')

local source = assert(debug.getinfo(1, 'S').source)
local script = assert(source:match('^@(.+)$'), 'run.lua must be loaded from a file')
local dir = assert(script:match('^(.*[/\\])'), 'run.lua has no directory')
local runner = dofile(dir .. '../../lua/sample.lua')
local port = tonumber(os.getenv('SAMPLE_PORT')) or 12121

local server = assert(socket.tcp_server('127.0.0.1', port, function(client)
    local data = client:sysread(1024)
    if data ~= nil then client:syswrite(data) end
end))
local ok, err = xpcall(function()
    runner.run(dir .. 'dist/adder.wasm', runner.default_options({
        args = {tostring(port)},
        inherit_network = true,
        allowed_ips = {'127.0.0.1'},
        allowed_ports = {port},
    }))
end, debug.traceback)
server:close()
if not ok then error(err, 0) end
print(('RAW GO WASI NETWORK PASSED on port %d'):format(port))
