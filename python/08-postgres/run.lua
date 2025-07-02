local source = assert(debug.getinfo(1, 'S').source)
local script = assert(source:match('^@(.+)$'), 'run.lua must be loaded from a file')
local dir = assert(script:match('^(.*[/\\])'), 'run.lua has no directory')
local runner = dofile(dir .. '../../lua/sample.lua')
local port = tonumber(os.getenv('POSTGRES_PORT')) or 5432
local user = os.getenv('POSTGRES_USER') or 'tarawasm'
local password = os.getenv('POSTGRES_PASSWORD') or 'tarawasm-password'
local database = os.getenv('POSTGRES_DB') or 'tarawasm'
local message = os.getenv('POSTGRES_MESSAGE') or 'hello from Python WASM'

runner.run(dir .. 'dist/adder.wasm', runner.default_options({
    args = {tostring(port), user, password, database, message},
    inherit_network = true,
    allowed_ips = {'127.0.0.1'},
    allowed_ports = {port},
    memory_limit = 256 * 1024 * 1024,
    max_instructions = 4 * 1000 * 1000 * 1000,
}))
