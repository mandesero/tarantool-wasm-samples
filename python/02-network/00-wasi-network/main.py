from wit_world import exports
from wit_world.imports import instance_network, log, network, poll, tarantool_tarantool_types as types, tcp, tcp_create_socket

import sys


def run_client(port: int) -> None:
    log.write(types.LogLevel.INFO, "PY | ===== Raw WASI TCP start =====", None)
    with instance_network.instance_network() as net:
        with tcp_create_socket.create_tcp_socket(network.IpAddressFamily.IPV4) as sock:
            peer = network.Ipv4SocketAddress(port=port, address=(127, 0, 0, 1))
            sock.start_connect(net, network.IpSocketAddress_Ipv4(peer))
            with sock.subscribe() as pollable:
                while not poll.poll([pollable]):
                    pollable.block()
            input_stream, output_stream = sock.finish_connect()
            with input_stream, output_stream:
                message = b"hello from raw Python WASI\n"
                output_stream.blocking_write_and_flush(message)
                echoed = input_stream.blocking_read(1024)
                if echoed != message:
                    raise RuntimeError(f"unexpected echo: {echoed!r}")
                log.write(types.LogLevel.INFO, f"PY | Echo: {echoed.decode().strip()}", None)
            sock.shutdown(tcp.ShutdownType.BOTH)
    log.write(types.LogLevel.INFO, "PY | ===== Raw WASI TCP done =====", None)


class Run(exports.Run):
    def run(self) -> None:
        try:
            run_client(int(sys.argv[0]) if sys.argv else 12121)
        except Exception as exc:
            print(f"RAW WASI ERROR: {exc!r}", flush=True)
            raise
