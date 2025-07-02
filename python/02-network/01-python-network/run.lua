local fiber = require('fiber')
local socket = require('socket')
local wasm = require('wasm')

local source = assert(debug.getinfo(1, 'S').source)
local script = assert(source:match('^@(.+)$'), 'run.lua must be loaded from a file')
local dir = assert(script:match('^(.*[/\\])'), 'run.lua has no directory')
local port = tonumber(os.getenv('SAMPLE_PORT')) or 65432
local modules = {}
local handles = {}

local function cleanup()
    for index, handle in pairs(handles) do
        pcall(wasm.cancel, handle)
        handles[index] = nil
    end
    for index, module_uid in pairs(modules) do
        pcall(wasm.drop, module_uid)
        modules[index] = nil
    end
end

local function options()
    return {
        args = {tostring(port)},
        inherit_env = false,
        inherit_stdin = false,
        inherit_network = true,
        allowed_ips = {'127.0.0.1'},
        allowed_ports = {port},
        memory_limit = 256 * 1024 * 1024,
        max_instructions = 2 * 1000 * 1000 * 1000,
    }
end

local ok, err = xpcall(function()
    modules.server = wasm.load(dir .. 'server/dist/adder.wasm', options())
    modules.client = wasm.load(dir .. 'client/dist/adder.wasm', options())
    handles.server = wasm.run(modules.server)

    local deadline = fiber.clock() + 10
    while true do
        local probe = socket.tcp_connect('127.0.0.1', port, 0.1)
        if probe ~= nil then
            probe:close()
            break
        end
        assert(fiber.clock() < deadline, 'TCP server readiness timeout')
        fiber.sleep(0.02)
    end

    handles.client = wasm.run(modules.client)
    assert(wasm.join(handles.client))
    handles.client = nil
    assert(wasm.join(handles.server))
    handles.server = nil
    assert(wasm.drop(modules.client))
    modules.client = nil
    assert(wasm.drop(modules.server))
    modules.server = nil
end, debug.traceback)

cleanup()
if not ok then error(err, 0) end
print(('TCP LIFECYCLE PASSED on port %d'):format(port))
