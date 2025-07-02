package main

import (
	"fmt"
	"encoding/json"
	"runtime"

	"adder-wasm-bindings/internal/wasi/cli/run"
	"adder-wasm-bindings/internal/tarantool/tarantool/say"
	"adder-wasm-bindings/internal/tarantool/tarantool/msgpack"
	"adder-wasm-bindings/internal/tarantool/tarantool/txn"
	tuple "adder-wasm-bindings/internal/tarantool/tarantool/box-tuple"
	box "adder-wasm-bindings/internal/tarantool/tarantool/ttbox"
	tarantoolTypes "adder-wasm-bindings/internal/tarantool/tarantool/types"
	"go.bytecodealliance.org/cm"
)

type LogContext = tarantoolTypes.LogContext
var LogContextNone = cm.None[LogContext]()

type Space = tarantoolTypes.Space
type Index = tarantoolTypes.Index
type BoxTuple = tarantoolTypes.BoxTuple

func init() {
	run.Exports.Run = wasiRun
}

func wasiRun() (result cm.BoolResult) {
	main()
	return
}

func Encode(obj interface{}) ([]byte, error) {
	jsonBytes, err := json.Marshal(obj)
	if err != nil {
		return nil, fmt.Errorf("error in JSON encoding: %v", err)
	}

	msgpackBytes := msgpack.Encode(cm.ToList(jsonBytes))
	if msgpackBytes.IsErr() {
		return nil, fmt.Errorf("error in msgpack encoding")
	}

	return msgpackBytes.OK().Slice(), nil
}

func Decode(data []byte) (interface{}, error) {
	decodedJsonBytes := msgpack.Decode(cm.ToList(data))
	if decodedJsonBytes.IsErr() {
		return nil, fmt.Errorf("error in msgpack decoding")
	}

	var obj interface{}
	err := json.Unmarshal(decodedJsonBytes.OK().Slice(), &obj)
	if err != nil {
		return nil, fmt.Errorf("error in JSON unmarshaling: %v", err)
	}

	return obj, nil
}

// TODO: https://github.com/mandesero/tarantool-wasm-rs/issues/3
func GetTupleSlice(ptr BoxTuple) ([]byte, error) {
	result := tuple.ToBuf(ptr)
	if result.IsOK() {
		tup := *result.OK()
		return tup.Slice(), nil
	}
	return nil, fmt.Errorf("error")
}

func batchInsert(space Space, batch [][]byte) {
	var ptr BoxTuple
	txn.Begin()
	for _, elem := range batch {
		result := box.Insert(space, cm.ToList(elem))
		if result.IsOK() {
			ptr = *result.OK()
			raw, _ := GetTupleSlice(ptr)
			tup, _ := Decode(raw)
			say.SayInfo(fmt.Sprintf("%v", tup), cm.Some(LogContext {Filename: "main.go", Line: 104}))
		}
	}
	txn.Commit()
}

func getLogContext() cm.Option[LogContext] {
	_, file, line, _ := runtime.Caller(1)
	return cm.Some(LogContext {
		Filename: file,
		Line: 	  uint32(line),
	})
}

func main() {
	var space Space
	result1 := box.SpaceByName("test_space")
	if result1.IsOK() {
		space = *result1.OK()
	}

	say.SayInfo(fmt.Sprintf("%v", space), cm.Some(LogContext {Filename: "main.go", Line: 125}))

	tuples := make([][]byte, 5)

	for idx := range 5 {
		tuples[idx], _ = Encode([]int{idx})
		t, _ := Decode(tuples[idx])
		say.SayInfo(fmt.Sprintf("%v", t), cm.Some(LogContext {Filename: "main.go", Line: 132}))
	}

	batchInsert(space, tuples)

}
