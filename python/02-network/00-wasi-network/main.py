from wit_world import exports
from wit_world.imports import (
    instance_network,
    ip_name_lookup,
    poll,
    tcp_create_socket,
    network,
    tcp,
    outgoing_handler,
    say,
)
from wit_world.types import Ok, Err
from wit_world.imports.wasi_http_types import (
    OutgoingRequest,
    RequestOptions,
    Method_Get,
    Fields,
    OutgoingBody,
)


# ================================
# IncomingHandler stub (no-op)
# ================================

class IncomingHandler(exports.IncomingHandler):
    def handle(self, request, response_out):
        """Stub handler (required by interface)."""
        pass


# ================================
# Test: DNS Resolve
# ================================

def network_test():
    say.say_info("PY | ===== Test resolve start =====", None)

    name = 'vk.com'
    net = instance_network.instance_network()

    resolver = ip_name_lookup.resolve_addresses(net, name)
    pollable = resolver.subscribe()
    pollables = [pollable]

    while True:
        ready_handles = poll.poll(pollables)
        if ready_handles:
            address = resolver.resolve_next_address()
            if address is None:
                break
            say.say_info(f"PY | Resolved address: {address}", None)
        else:
            pollable.block()

    say.say_info("PY | ===== Test resolve done =====", None)

    # ================================
    # Test: HTTP GET Request
    # ================================

    say.say_info("PY | ===== Test http start =====", None)

    opts = RequestOptions()
    opts.set_connect_timeout(5_000_000_000)
    opts.set_first_byte_timeout(5_000_000_000)
    opts.set_between_bytes_timeout(5_000_000_000)

    headers = Fields.from_list([
        ("User-Agent", b"MyWASIClient/1.0"),
    ])

    req = OutgoingRequest(headers)
    req.set_method(Method_Get())
    req.set_path_with_query("/")
    req.set_authority("vk.com")

    body = req.body()
    OutgoingBody.finish(body, None)

    future = outgoing_handler.handle(req, opts)
    pollable = future.subscribe()
    poll.poll([pollable])

    result = future.get()
    if result is None:
        say.say_warn("PY | HTTP request returned None", None)
    elif isinstance(result, Ok):
        resp = result.value.value
        say.say_info(f"PY | HTTP status: {resp.status()}", None)

        hdrs = resp.headers().entries()
        for name, val in hdrs:
            say.say_info(f"PY | Header: {name} = {val.decode()}", None)
    elif isinstance(result, Err):
        say.say_error(f"PY | HTTP client error: {result.value}", None)

    say.say_info("PY | ===== Test http done =====", None)

    # ================================
    # Test: TCP Connect and Echo
    # ================================

    say.say_info("PY | ===== Test connect start =====", None)

    net = instance_network.instance_network()
    peer = network.Ipv4SocketAddress(port=12121, address=(127, 0, 0, 1))

    socket = tcp_create_socket.create_tcp_socket(network.IpAddressFamily.IPV4)
    pollable = socket.subscribe()
    pollables = [pollable]

    socket.start_connect(net, network.IpSocketAddress_Ipv4(peer))

    while True:
        ready_handles = poll.poll(pollables)
        if ready_handles:
            in_s, out_s = socket.finish_connect()

            # Send message
            out_s.blocking_write_and_flush("hello from python wasm\n".encode())

            # Receive response
            msg = in_s.blocking_read(1024)
            say.say_info(f"PY | Msg from server: {msg}", None)

            # Shutdown connection
            socket.shutdown(tcp.ShutdownType.BOTH)
            break
        else:
            pollable.block()

    say.say_info("PY | ===== Test connect done =====", None)


# ================================
# WASM entry point
# ================================

class Run(exports.Run):
    def run(self) -> None:
        try:
            network_test()
        except Exception as e:
            say.say_error(str(e), None)
