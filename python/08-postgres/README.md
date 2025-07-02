# PostgreSQL with pg8000

Uses the ready-made pure-Python `pg8000` DB-API client without native `libpq`.
The guest authenticates with SCRAM-SHA-256, creates a temporary table, performs
a parameterized insert with `RETURNING`, commits, reads the row back, and closes
both cursor and connection deterministically.

Complete the [root setup](https://github.com/mandesero/tarantool-wasm-samples),
then run the fully automated local integration test:

```sh
make postgres-image
make build SAMPLE=python/08-postgres
make postgres-smoke
```

The test starts pinned PostgreSQL 17.6 on a free loopback port, waits with
`pg_isready`, runs the component, and removes the container. Expected output:

```text
PYTHON PG8000 ROUNDTRIP: id=1 body=pg8000 message ...
POSTGRESQL INTEGRATION PASSED on released port ...
```

To use an existing plaintext PostgreSQL server whose listener is reachable at
loopback, provide its connection settings explicitly:

```sh
POSTGRES_PORT=5432 \
POSTGRES_USER=tarawasm \
POSTGRES_PASSWORD='secret' \
POSTGRES_DB=tarawasm \
POSTGRES_MESSAGE='hello from Python WASM' \
make run SAMPLE=python/08-postgres
```

`pg8000` and transitive packages are pinned in `requirements.txt`. Current
componentize Python lacks the `ssl` module, so this sample explicitly disables
TLS and must not be pointed at an untrusted network. It also lacks
`hashlib.pbkdf2_hmac`; `pbkdf2_compat.py` provides only that missing standard
function so the unmodified pg8000/scramp stack can use modern SCRAM-SHA-256.
The fallback is checked against CPython's implementation during repository
verification. Error paths roll back the transaction before closing resources.
