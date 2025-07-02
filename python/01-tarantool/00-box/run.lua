local source = assert(debug.getinfo(1, 'S').source)
local script = assert(source:match('^@(.+)$'), 'run.lua must be loaded from a file')
local dir = assert(script:match('^(.*[/\\])'), 'run.lua has no directory')
local runner = dofile(dir .. '../../../lua/sample.lua')

box.cfg{log_level = 5}
local space = box.schema.space.create('test_space', {if_not_exists = true})
space:create_index('primary', {parts = {{1, 'unsigned'}}, if_not_exists = true})
runner.run(dir .. 'dist/adder.wasm', runner.default_options())

os.exit(0)
