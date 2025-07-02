# PostgreSQL over WASI TLS with pg8000

This sample keeps the ready-made pure-Python pg8000 DB-API client and maps
the synchronous socket/SSLContext subset it consumes to host-provided
wasi:tls resources. Cryptography, SNI, and certificate validation run in
wasm.so rather than a guest OpenSSL build.

Complete the [root setup](https://github.com/mandesero/tarantool-wasm-samples),
then build the component and verify a real encrypted round-trip against a
publicly trusted TLS endpoint:

```sh
make build SAMPLE=python/13-postgres-tls
make postgres-tls-smoke
```

Expected output:

```text
PYTHON WASI TLS ROUNDTRIP: HTTP/1.1 200 OK
```

Run the pg8000 transaction against a TLS-enabled PostgreSQL server by
supplying its allowed IPv4 destination separately from the certificate DNS
name used for SNI and hostname validation:

```sh
POSTGRES_HOST=203.0.113.10 \
POSTGRES_TLS_SERVER_NAME=db.example.com \
POSTGRES_PORT=5432 \
POSTGRES_USER=tarawasm \
POSTGRES_PASSWORD=secret \
POSTGRES_DB=tarawasm \
POSTGRES_MESSAGE="hello over TLS" \
make run SAMPLE=python/13-postgres-tls
```

The current wasi:tls@0.2.0-draft trusts the WebPKI roots embedded in wasm.so.
It does not expose custom CA bundles, client certificates, peer certificates,
or TLS channel binding. A local self-signed PostgreSQL certificate therefore
cannot be accepted, and pg8000 uses SCRAM without -PLUS.

Componentize Python still has no general _ssl module. wasi_tls_socket.py is a
deliberately narrow synchronous adapter for this sample, not a drop-in stdlib
ssl implementation. Error paths close the transport, and the host joins and
drops the component deterministically.
