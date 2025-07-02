local source = assert(debug.getinfo(1, 'S').source)
local script = assert(source:match('^@(.+)$'), 'run.lua must be loaded from a file')
local dir = assert(script:match('^(.*[/\\])'), 'run.lua has no directory')
local runner = dofile(dir .. '../../../lua/sample.lua')

box.cfg{log_level = 5}
runner.run(dir .. 'dist/adder.wasm', runner.default_options())

os.exit(0)
