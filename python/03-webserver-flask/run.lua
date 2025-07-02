local fiber = require('fiber')
local socket = require('socket')
local wasm = require('wasm')

local source = assert(debug.getinfo(1, 'S').source)
local script = assert(source:match('^@(.+)$'), 'run.lua must be loaded from a file')
local dir = assert(script:match('^(.*[/\\])'), 'run.lua has no directory')
local port = tonumber(os.getenv('SAMPLE_PORT')) or 8080
local callback_name = 'http-handler'

local module_uid
local handle
local registered = false

local function cleanup()
    if registered then
        pcall(wasm.unregister_callback, callback_name)
        registered = false
    end
    if handle ~= nil then
        pcall(wasm.cancel, handle)
        handle = nil
    end
    if module_uid ~= nil then
        pcall(wasm.drop, module_uid)
        module_uid = nil
    end
end

local function connect()
    return socket.tcp_connect('127.0.0.1', port, 0.1)
end

local function wait_ready()
    -- Flask import and component startup can take longer on a cold CI host.
    local deadline = fiber.clock() + 30
    repeat
        local client = connect()
        if client ~= nil then
            client:close()
            return
        end
        fiber.sleep(0.02)
    until fiber.clock() >= deadline
    error(('HTTP guest did not listen on port %d'):format(port))
end

local function request(path, method)
    method = method or 'GET'
    local client
    local connect_deadline = fiber.clock() + 2
    repeat
        client = connect()
        if client == nil then fiber.sleep(0.01) end
    until client ~= nil or fiber.clock() >= connect_deadline
    assert(client, ('cannot connect to port %d'):format(port))
    local crlf = string.char(13, 10)
    local request_text = ('%s %s HTTP/1.0%sHost: localhost%sContent-Length: 0%s%s'):format(method, path, crlf, crlf, crlf, crlf)
    assert(client:syswrite(request_text))
    local response = ''
    local header_end
    while header_end == nil do
        local chunk = assert(client:read({chunk = 4096}), 'HTTP response ended before headers')
        response = response .. chunk
        header_end = response:find('\r\n\r\n', 1, true)
    end
    local headers = response:sub(1, header_end + 3)
    local content_length = tonumber(headers:match('[Cc]ontent%-[Ll]ength:%s*(%d+)')) or 0
    local body_start = header_end + 4
    while #response - body_start + 1 < content_length do
        response = response .. assert(client:read({chunk = content_length}), 'HTTP response body was truncated')
    end
    client:close()
    return response
end

local ok, err = xpcall(function()
    local options = {
        args = {tostring(port)},
        inherit_env = false,
        inherit_stdin = false,
        inherit_network = true,
        allowed_ips = {'127.0.0.1'},
        allowed_ports = {port},
        memory_limit = 512 * 1024 * 1024,
        max_instructions = 5 * 1000 * 1000 * 1000,
    }
    module_uid = wasm.load(dir .. 'dist/adder.wasm', options)

    -- The guest opens its handler resource before this closure exists.
    handle = wasm.run(module_uid)
    local deadline = fiber.clock() + 30
    while true do
        local requested, response = pcall(request, '/before-registration')
        if requested and response:find('is not registered', 1, true) then
            assert(response:find(' 503 ', 1, true), response)
            print('PRE-REGISTRATION RESPONSE: 503 Service Unavailable')
            break
        end
        assert(fiber.clock() < deadline, 'HTTP guest readiness timeout')
        fiber.sleep(0.02)
    end

    assert(wasm.register_callback(callback_name, function(req)
        return {status = 200, body = 'first handler: ' .. req.path .. '\n'}
    end, {timeout_ms = 250}))
    registered = true
    local first = request('/first')
    assert(first:find('first handler: /first', 1, true), first)
    print('FIRST RESPONSE: first handler: /first')

    assert(wasm.register_callback(callback_name, function(req)
        return {status = 200, body = 'replacement handler: ' .. req.path .. '\n'}
    end, {timeout_ms = 250}))
    local second = request('/second')
    assert(second:find('replacement handler: /second', 1, true), second)
    print('REPLACED RESPONSE: replacement handler: /second')

    assert(wasm.unregister_callback(callback_name))
    registered = false
    local missing = request('/missing')
    assert(missing:find(' 503 ', 1, true), missing)
    assert(missing:find('is not registered', 1, true), missing)
    print('UNREGISTERED RESPONSE: 503 Service Unavailable')

    local stopped = request('/__shutdown', 'POST')
    assert(stopped:find(' 200 ', 1, true), stopped)
    assert(wasm.join(handle))
    handle = nil
    assert(wasm.drop(module_uid))
    module_uid = nil
end, debug.traceback)

cleanup()
if not ok then
    error(err, 0)
end
print(('HTTP CALLBACK DEMO PASSED on port %d'):format(port))
