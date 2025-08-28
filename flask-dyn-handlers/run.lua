local luawasm = require('luawasm')

luawasm.wasm.set_handler("./dyn_handler/libhandlers.so", "/hello")
luawasm.wasm.set_handler("./dyn_handler/libhandlers.so", "/echo")
luawasm.wasm.set_handler("./dyn_handler/libhandlers.so", "/bin")
