"""Small synchronous socket facade backed by WASI sockets and WASI TLS.

This deliberately implements only the methods used by pg8000. Cryptography,
certificate validation, and SNI remain in the host's wasi:tls provider.
"""

from wit_world.imports import (
    instance_network,
    monotonic_clock,
    network,
    poll as wasi_poll,
    tcp,
    tcp_create_socket,
    types as tls,
)
from componentize_py_types import Err


_NONE_UNPACK_ERROR = "cannot unpack non-iterable NoneType object"
_RESOURCES = []


def _keep(*resources):
    # componentize-py 0.25 can trap while dropping moved resource handles.
    # The component store releases these after wasi:cli/run returns.
    _RESOURCES.extend(resource for resource in resources if resource is not None)


def _parse_ipv4(host):
    parts = host.split(".")
    if len(parts) != 4:
        raise ValueError("WASI TLS socket currently requires an IPv4 address")
    octets = tuple(int(part) for part in parts)
    if any(value < 0 or value > 255 for value in octets):
        raise ValueError(f"invalid IPv4 address: {host}")
    return octets


def _deadline_after(timeout_seconds):
    return monotonic_clock.now() + int(timeout_seconds * 1_000_000_000)


def _remaining(deadline):
    now = monotonic_clock.now()
    return max(0, deadline - now)


def _wait_ready(target, deadline, operation):
    remaining = _remaining(deadline)
    if remaining == 0:
        raise TimeoutError(f"{operation} timed out")
    timer = monotonic_clock.subscribe_duration(remaining)
    _keep(timer)
    if 0 not in wasi_poll.poll([target, timer]):
        raise TimeoutError(f"{operation} timed out")


def _is_transient_none(error):
    return isinstance(error, TypeError) and _NONE_UNPACK_ERROR in str(error)


class WasiSocketFile:
    def __init__(self, sock):
        self._socket = sock

    def read(self, size=-1):
        if size is None or size < 0:
            raise ValueError("unbounded reads are not supported")
        chunks = []
        remaining = size
        while remaining:
            chunk = self._socket.recv(remaining)
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        return b"".join(chunks)

    def write(self, data):
        self._socket.sendall(data)
        return len(data)

    def flush(self):
        return None

    def close(self):
        return None


class WasiTlsSocket:
    def __init__(self, host, port, timeout=10):
        self._timeout = timeout
        self._closed = False
        self._connection = None

        address = _parse_ipv4(host)
        net = instance_network.instance_network()
        sock = tcp_create_socket.create_tcp_socket(network.IpAddressFamily.IPV4)
        _keep(net, sock)

        remote = network.Ipv4SocketAddress(port=port, address=address)
        sock.start_connect(net, network.IpSocketAddress_Ipv4(remote))
        connect_pollable = sock.subscribe()
        _keep(connect_pollable)
        deadline = _deadline_after(timeout)

        while True:
            _wait_ready(connect_pollable, deadline, "TCP connect")
            try:
                connected = sock.finish_connect()
            except TypeError as error:
                if _is_transient_none(error):
                    continue
                raise
            except Err as error:
                if error.value == network.ErrorCode.WOULD_BLOCK:
                    continue
                raise OSError(f"WASI TCP connect failed: {error.value.name}") from error
            if connected is not None:
                break

        self._socket = sock
        self._input, self._output = connected
        _keep(self._input, self._output)

    def start_tls(self, server_name):
        if self._closed:
            raise OSError("socket is closed")
        handshake = tls.ClientHandshake(server_name, self._input, self._output)
        _keep(handshake)
        deadline = _deadline_after(self._timeout)

        while True:
            try:
                future = tls.ClientHandshake.finish(handshake)
                _keep(future)
                break
            except TypeError as error:
                if _is_transient_none(error):
                    if _remaining(deadline) == 0:
                        raise TimeoutError("TLS handshake start timed out") from error
                    continue
                raise

        pollable = future.subscribe()
        _keep(pollable)
        while True:
            _wait_ready(pollable, deadline, "TLS handshake")
            try:
                result = future.get()
            except TypeError as error:
                if _is_transient_none(error):
                    continue
                raise
            if result is None:
                continue
            if isinstance(result, Err):
                raise OSError("WASI TLS future was cancelled")
            inner = result.value
            if isinstance(inner, Err):
                raise OSError(
                    "WASI TLS handshake failed: " + inner.value.to_debug_string()
                )
            self._connection, self._input, self._output = inner.value
            _keep(self._connection, self._input, self._output)
            return self

    def sendall(self, data):
        if self._closed:
            raise OSError("socket is closed")
        self._output.blocking_write_and_flush(bytes(data))

    def recv(self, size):
        if self._closed:
            return b""
        try:
            return self._input.blocking_read(size)
        except Err as error:
            value = error.value
            if value.__class__.__name__.endswith("Closed"):
                return b""
            raise OSError(f"WASI stream read failed: {value!r}") from error

    def makefile(self, mode="rwb"):
        if mode != "rwb":
            raise ValueError(f"unsupported socket file mode: {mode}")
        return WasiSocketFile(self)

    def setsockopt(self, *_args):
        return None

    def close(self):
        if self._closed:
            return
        self._closed = True
        if self._connection is not None:
            self._connection.close_output()
            return
        try:
            self._socket.shutdown(tcp.ShutdownType.BOTH)
        except Err:
            pass


class WasiTlsContext:
    """The SSLContext subset consumed by pg8000."""

    def __init__(self, server_name=None):
        self._server_name = server_name

    def wrap_socket(self, sock, server_hostname=None):
        name = self._server_name or server_hostname
        if not name:
            raise ValueError("TLS server name is required")
        wrapped = sock.start_tls(name)
        print(f"PYTHON PG8000 TLS ESTABLISHED: server_name={name}")
        return wrapped


def connect(host, port, timeout=10):
    return WasiTlsSocket(host, port, timeout)
