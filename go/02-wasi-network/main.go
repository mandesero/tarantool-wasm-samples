package main

import (
	"fmt"
	"os"
	"strconv"

	"adder-wasm-bindings/internal/wasi/cli/run"
	"adder-wasm-bindings/internal/wasi/io/poll"
	instNet "adder-wasm-bindings/internal/wasi/sockets/instance-network"
	wasiNet "adder-wasm-bindings/internal/wasi/sockets/network"
	tcpSocket "adder-wasm-bindings/internal/wasi/sockets/tcp-create-socket"
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
	port := uint16(12121)
	if len(os.Args) > 0 {
		value, err := strconv.ParseUint(os.Args[0], 10, 16)
		if err != nil {
			panic(err)
		}
		port = uint16(value)
	}

	net := instNet.InstanceNetwork()
	defer net.ResourceDrop()
	created := tcpSocket.CreateTCPSocket(wasiNet.IPAddressFamilyIPv4)
	if created.IsErr() {
		panic("cannot create TCP socket")
	}
	sock := *created.OK()
	defer sock.ResourceDrop()
	peer := wasiNet.IPv4SocketAddress{
		Port:    port,
		Address: wasiNet.IPv4Address{127, 0, 0, 1},
	}
	started := sock.StartConnect(net, wasiNet.IPSocketAddressIPv4(peer))
	if started.IsErr() {
		panic("connection start failed")
	}
	func() {
		pollable := sock.Subscribe()
		defer pollable.ResourceDrop()
		for len(poll.Poll(cm.ToList([]poll.Pollable{pollable})).Slice()) == 0 {
			pollable.Block()
		}
	}()

	connected := sock.FinishConnect()
	if connected.IsErr() {
		panic("connection failed")
	}
	inStream := connected.OK().F0
	outStream := connected.OK().F1
	defer inStream.ResourceDrop()
	defer outStream.ResourceDrop()

	message := "hello from raw Go WASI\n"
	written := outStream.BlockingWriteAndFlush(cm.ToList([]uint8(message)))
	if written.IsErr() {
		panic(fmt.Sprintf("echo write failed: %#v", *written.Err()))
	}
	received := make([]byte, 0, len(message))
	for len(received) < len(message) {
		read := inStream.BlockingRead(uint64(len(message) - len(received)))
		if read.IsErr() {
			panic(fmt.Sprintf("echo read failed: %#v", *read.Err()))
		}
		chunk := read.OK().Slice()
		if len(chunk) == 0 {
			panic("echo read failed: unexpected EOF")
		}
		received = append(received, chunk...)
	}
	response := string(received)
	if response != message {
		panic(fmt.Sprintf("echo mismatch: got %q, want %q", response, message))
	}
	fmt.Printf("GO RAW ECHO: %s", response)
	shutdown := sock.Shutdown(2)
	if shutdown.IsErr() {
		panic(fmt.Sprintf("socket shutdown failed: %#v", *shutdown.Err()))
	}
}
