"""Minimal SSL names required by Paho's plaintext socket code."""

import types


class SSLWantReadError(BlockingIOError):
    pass


class SSLWantWriteError(BlockingIOError):
    pass


class CertificateError(Exception):
    pass


class SSLContext:
    def __init__(self, *_args, **_kwargs) -> None:
        raise RuntimeError(
            "TLS is unavailable in this componentize Python build; "
            "use a plaintext loopback MQTT endpoint"
        )


def create_default_context(*_args, **_kwargs):
    return SSLContext()


def install(client_module) -> None:
    client_module.ssl = types.SimpleNamespace(
        CERT_NONE=0,
        CERT_REQUIRED=2,
        CertificateError=CertificateError,
        PROTOCOL_TLS=2,
        PROTOCOL_TLS_CLIENT=16,
        PROTOCOL_TLSv1_2=5,
        SSLContext=SSLContext,
        SSLSocket=object,
        SSLWantReadError=SSLWantReadError,
        SSLWantWriteError=SSLWantWriteError,
        VerifyMode=int,
        create_default_context=create_default_context,
    )
