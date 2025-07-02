package main

import (
	"fmt"

	"adder-wasm-bindings/internal/wasi/cli/run"
	"go.bytecodealliance.org/cm"
)

func init() {
	run.Exports.Run = wasiRun
}

func wasiRun() (result cm.BoolResult) {
	main()
	return
}

func main() {
	fmt.Println("Hello from Go WASM!")
}
