"""Import-only SSL compatibility for plaintext WebSocket connections."""

import sys
import types


def install() -> None:
    try:
        import ssl  # noqa: F401
    except ModuleNotFoundError:
        module = types.ModuleType("ssl")

        class SSLContext:
            pass

        def create_default_context(*_args, **_kwargs):
            raise RuntimeError(
                "TLS is unavailable in this componentize Python build; "
                "use a plaintext loopback ws:// endpoint"
            )

        module.SSLContext = SSLContext
        module.create_default_context = create_default_context
        sys.modules["ssl"] = module
