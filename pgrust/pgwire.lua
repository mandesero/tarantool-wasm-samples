local M = {}

local function u16(value)
    return string.char(math.floor(value / 256) % 256, value % 256)
end

local function u32(value)
    return string.char(
        math.floor(value / 16777216) % 256,
        math.floor(value / 65536) % 256,
        math.floor(value / 256) % 256,
        value % 256
    )
end

local function read_u16(data, pos)
    local a, b = data:byte(pos, pos + 1)
    return a * 256 + b, pos + 2
end

local function read_u32(data, pos)
    local a, b, c, d = data:byte(pos, pos + 3)
    return ((a * 256 + b) * 256 + c) * 256 + d, pos + 4
end

local function cstring(data, pos)
    local stop = assert(data:find('\0', pos, true), 'unterminated pgwire string')
    return data:sub(pos, stop - 1), stop + 1
end

local Session = {}
Session.__index = Session

function Session:_read_exact(size)
    while #self.buffer < size do
        local chunk, eof = self.pipe:read({max_bytes = math.max(65536, size), timeout_ms = self.timeout_ms})
        if eof then error('unexpected EOF from pgrust') end
        self.buffer = self.buffer .. chunk
    end
    local value = self.buffer:sub(1, size)
    self.buffer = self.buffer:sub(size + 1)
    return value
end

function Session:_message()
    local kind = self:_read_exact(1)
    local length = read_u32(self:_read_exact(4), 1)
    return kind, self:_read_exact(length - 4)
end

local function error_fields(body)
    local fields, pos = {}, 1
    while body:byte(pos) ~= 0 do
        local kind = body:sub(pos, pos)
        fields[kind], pos = cstring(body, pos + 1)
    end
    return fields
end

function M.open(module, config, options)
    options = options or {}
    local pipe = require('wasm').pipe.spawn(module, config, {
        capacity = options.capacity or 1024 * 1024,
    })
    local self = setmetatable({
        pipe = pipe,
        buffer = '',
        timeout_ms = options.timeout_ms or 30000,
        parameters = {},
    }, Session)
    local ok, err = xpcall(function()
        local startup = u32(196608) .. 'user\0postgres\0database\0postgres\0client_encoding\0UTF8\0\0'
        assert(pipe:write(u32(#startup + 4) .. startup, {timeout_ms = self.timeout_ms}))
        while true do
            local kind, body = self:_message()
            if kind == 'R' then
                local method = read_u32(body, 1)
                assert(method == 0, 'unsupported PostgreSQL authentication method: ' .. method)
            elseif kind == 'S' then
                local key, pos = cstring(body, 1)
                self.parameters[key] = cstring(body, pos)
            elseif kind == 'E' then
                local fields = error_fields(body)
                error(fields.M or 'PostgreSQL startup error')
            elseif kind == 'Z' then
                self.transaction_status = body
                return
            end
        end
    end, debug.traceback)
    if not ok then
        local close_ok, close_err = pcall(pipe.close, pipe, {timeout_ms = self.timeout_ms})
        if not close_ok then
            error(('%s\npipe cleanup failed: %s'):format(err, close_err))
        end
        error(err)
    end
    return self
end

function Session:query(sql)
    assert(self.pipe:write('Q' .. u32(#sql + 5) .. sql .. '\0', {timeout_ms = self.timeout_ms}))
    local result = {columns = {}, rows = {}, notices = {}}
    while true do
        local kind, body = self:_message()
        if kind == 'T' then
            local count, pos = read_u16(body, 1)
            for i = 1, count do
                result.columns[i], pos = cstring(body, pos)
                pos = pos + 18
            end
        elseif kind == 'D' then
            local count, pos = read_u16(body, 1)
            local row = {}
            for i = 1, count do
                local size
                size, pos = read_u32(body, pos)
                if size == 4294967295 then
                    row[i] = nil
                else
                    row[i] = body:sub(pos, pos + size - 1)
                    pos = pos + size
                end
            end
            result.rows[#result.rows + 1] = row
        elseif kind == 'C' then
            result.command = cstring(body, 1)
        elseif kind == 'N' then
            result.notices[#result.notices + 1] = error_fields(body)
        elseif kind == 'E' then
            local fields = error_fields(body)
            error(fields.M or 'PostgreSQL query error')
        elseif kind == 'Z' then
            self.transaction_status = body
            return result
        end
    end
end

function Session:close()
    if self.closed then return true end
    local ok, err = xpcall(function()
        assert(self.pipe:write('X' .. u32(4), {timeout_ms = self.timeout_ms}))
        assert(self.pipe:close_stdin())
        assert(self.pipe:join({timeout_ms = self.timeout_ms}))
    end, debug.traceback)
    if ok then
        self.closed = true
        return true
    end
    local close_ok, close_err = pcall(self.pipe.close, self.pipe,
                                      {timeout_ms = self.timeout_ms})
    if close_ok then
        self.closed = true
        error(err)
    end
    error(('%s\npipe cleanup failed: %s'):format(err, close_err))
end

M.Session = Session
return M
