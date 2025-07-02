local wasm = require('wasm')

local M = {}

function M.script_dir(level)
    local info = debug.getinfo((level or 1) + 1, 'S')
    local source = assert(info and info.source, 'cannot determine script path')
    assert(source:sub(1, 1) == '@', 'run.lua must be loaded from a file')
    return assert(source:sub(2):match('^(.*[/\\])'), 'run.lua has no directory')
end

function M.default_options(extra)
    local options = {
        inherit_env = false,
        inherit_stdin = false,
        inherit_network = false,
        memory_limit = 256 * 1024 * 1024,
        max_instructions = 2 * 1000 * 1000 * 1000,
    }
    for key, value in pairs(extra or {}) do
        options[key] = value
    end
    return options
end

function M.run(component_path, options)
    local module_uid = wasm.load(component_path, options or M.default_options())
    local handle
    local consumed = false

    local ok, err = xpcall(function()
        handle = wasm.run(module_uid)
        assert(wasm.join(handle))
        consumed = true
    end, debug.traceback)

    if handle ~= nil and not consumed then
        pcall(wasm.cancel, handle)
    end

    local dropped, drop_err = pcall(wasm.drop, module_uid)
    if not ok then
        error(err, 0)
    end
    if not dropped then
        error(drop_err, 0)
    end
    return true
end

function M.drop_all(module_uids)
    local errors = {}
    for _, module_uid in ipairs(module_uids) do
        local ok, err = pcall(wasm.drop, module_uid)
        if not ok then
            table.insert(errors, tostring(err))
        end
    end
    if #errors > 0 then
        error(table.concat(errors, '; '), 0)
    end
end

return M
