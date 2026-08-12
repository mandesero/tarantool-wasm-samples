local wasm = require('wasm')

local root = assert(os.getenv('PGRUST_SAMPLE_ROOT'),
                    'PGRUST_SAMPLE_ROOT is not set')
local runtime = os.getenv('PGRUST_RUNTIME_ROOT') or (root .. '/runtime')

package.path = root .. '/?.lua;' .. package.path
local pgwire = require('pgwire')

local function read_file(path)
    local file = assert(io.open(path, 'r'))
    local contents = file:read('*a')
    file:close()
    return contents
end

local config = {
    inherit_env = false,
    env = {
        USER = 'postgres',
        PGRUST_PGSHAREDIR = '/share',
        PGRUST_TZDIR = '/zoneinfo',
        PGRUST_RUNTIME = '0',
        RUST_MIN_STACK = '67108864',
    },
    inherit_args = false,
    args = {
        'postgres', '--stdio-wire', '-D', '/pgdata',
        '-c', 'io_method=sync', '-c', 'autovacuum=off',
        '-c', 'wal_sync_method=fdatasync',
        '-c', 'shared_buffers=32MB', '-c', 'max_connections=10',
        '-c', 'max_stack_depth=60000',
    },
    inherit_network = false,
    allow_ip_name_lookup = false,
    allow_tcp = false,
    allow_udp = false,
    preopened_dirs = {
        {runtime .. '/pgdata', '/pgdata', perms = 'rw'},
        {runtime .. '/share', '/share', perms = 'ro'},
        {runtime .. '/zoneinfo', '/zoneinfo', perms = 'ro'},
    },
    memory_limit = 512 * 1024 * 1024,
}

local module
local session

local ok, err = xpcall(function()
    module = assert(wasm.load(root .. '/artifacts/pgrust.component.wasm',
                              config))
    session = pgwire.open(module, nil)

    local setup = session:query(read_file(root .. '/smoke.sql'))
    assert(setup.command == 'COMMIT', setup.command)

    local result = session:query([[
        SELECT id, product, quantity, price * quantity AS total
        FROM inventory
        WHERE quantity > 0
        ORDER BY id
    ]])
    assert(result.command == 'SELECT 3', result.command)

    local expected_columns = {'id', 'product', 'quantity', 'total'}
    for i, name in ipairs(expected_columns) do
        assert(result.columns[i] == name, result.columns[i])
    end

    local expected_rows = {
        {'1', 'keyboard', '3', '15000'},
        {'2', 'mouse', '7', '10500'},
        {'4', 'webcam', '2', '14000'},
    }
    assert(#result.rows == #expected_rows, #result.rows)

    for i, expected in ipairs(expected_rows) do
        local row = result.rows[i]
        for column, value in ipairs(expected) do
            assert(row[column] == value, row[column])
        end
        print(('id=%s product=%s quantity=%s total=%s'):format(
            row[1], row[2], row[3], row[4]))
    end
end, debug.traceback)

local cleanup_errors = {}
if session then
    local close_ok, close_err = pcall(session.close, session)
    if not close_ok then cleanup_errors[#cleanup_errors + 1] = close_err end
end
if module then
    local drop_ok, drop_err = pcall(wasm.drop, module)
    if not drop_ok then cleanup_errors[#cleanup_errors + 1] = drop_err end
end

if not ok then
    if #cleanup_errors > 0 then
        err = err .. '\ncleanup failed: ' .. table.concat(cleanup_errors, '; ')
    end
    error(err)
end
assert(#cleanup_errors == 0, table.concat(cleanup_errors, '; '))
print('PGRUST_PIPE_QUERY_OK')
