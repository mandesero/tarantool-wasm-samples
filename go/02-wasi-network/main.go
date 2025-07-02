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
	pollable := sock.Subscribe()
	defer pollable.ResourceDrop()

	peer := wasiNet.IPv4SocketAddress{
		Port:    port,
		Address: wasiNet.IPv4Address{127, 0, 0, 1},
	}
	sock.StartConnect(net, wasiNet.IPSocketAddressIPv4(peer))
	for len(poll.Poll(cm.ToList([]poll.Pollable{pollable})).Slice()) == 0 {
		pollable.Block()
	}

	connected := sock.FinishConnect()
	if connected.IsErr() {
		panic("connection failed")
	}
	inStream := connected.OK().F0
	outStream := connected.OK().F1
	defer inStream.ResourceDrop()
	defer outStream.ResourceDrop()

	message := "hello from raw Go WASI\n"
	outStream.BlockingWriteAndFlush(cm.ToList([]uint8(message)))
	read := inStream.BlockingRead(1024)
	if read.IsErr() {
		panic("echo read failed")
	}
	fmt.Printf("GO RAW ECHO: %s", string(read.OK().Slice()))
	sock.Shutdown(2)
}
