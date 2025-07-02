package main

import (
	"encoding/json"
	"fmt"

	tuple "adder-wasm-bindings/internal/tarantool/tarantool/box-tuple"
	"adder-wasm-bindings/internal/tarantool/tarantool/database"
	"adder-wasm-bindings/internal/tarantool/tarantool/log"
	"adder-wasm-bindings/internal/tarantool/tarantool/msgpack"
	"adder-wasm-bindings/internal/tarantool/tarantool/transaction"
	tarantoolTypes "adder-wasm-bindings/internal/tarantool/tarantool/types"
	"adder-wasm-bindings/internal/wasi/cli/run"
	"go.bytecodealliance.org/cm"
)

type LogContext = tarantoolTypes.LogContext
type MsgpackValue = tarantoolTypes.MsgpackValue

func init() {
	run.Exports.Run = wasiRun
}

func wasiRun() (result cm.BoolResult) {
	if err := runSample(); err != nil {
		logMessage(tarantoolTypes.LogLevelError, fmt.Sprintf("GO | %v", err))
	}
	return
}

func logMessage(level tarantoolTypes.LogLevel, message string) {
	log.Write(level, message, cm.None[LogContext]())
}

func encode(value any) (MsgpackValue, error) {
	data, err := json.Marshal(value)
	if err != nil {
		return MsgpackValue{}, err
	}
	result := msgpack.FromJSON(string(data))
	if result.IsErr() {
		return MsgpackValue{}, fmt.Errorf("msgpack.from-json: %v", *result.Err())
	}
	return *result.OK(), nil
}

func consumeTuple(value tarantoolTypes.BoxTuple) (string, error) {
	defer tuple.Release(value)
	bytesResult := tuple.ToBytes(value)
	if bytesResult.IsErr() {
		return "", fmt.Errorf("box-tuple.to-bytes: %v", *bytesResult.Err())
	}
	jsonResult := msgpack.ToJSON(*bytesResult.OK())
	if jsonResult.IsErr() {
		return "", fmt.Errorf("msgpack.to-json: %v", *jsonResult.Err())
	}
	return *jsonResult.OK(), nil
}

func runSample() error {
	spaceResult := database.SpaceByName("test_space")
	if spaceResult.IsErr() {
		return fmt.Errorf("space lookup: %v", *spaceResult.Err())
	}
	spacePointer := spaceResult.OK().Some()
	if spacePointer == nil {
		return fmt.Errorf("space not found: test_space")
	}
	space := *spacePointer
	logMessage(tarantoolTypes.LogLevelInfo, fmt.Sprintf("GO | Space: %v", space))

	if started := transaction.Begin(); started.IsErr() {
		return fmt.Errorf("transaction begin: %v", *started.Err())
	}
	committed := false
	defer func() {
		if !committed {
			transaction.Rollback()
		}
	}()

	for value := range 5 {
		encoded, err := encode([]int{value})
		if err != nil {
			return err
		}
		inserted := database.Insert(space, encoded)
		if inserted.IsErr() {
			return fmt.Errorf("insert %d: %v", value, *inserted.Err())
		}
		decoded, err := consumeTuple(*inserted.OK())
		if err != nil {
			return err
		}
		logMessage(tarantoolTypes.LogLevelInfo, decoded)
	}

	if commit := transaction.Commit(); commit.IsErr() {
		return fmt.Errorf("transaction commit: %v", *commit.Err())
	}
	committed = true
	return nil
}

func main() {}
