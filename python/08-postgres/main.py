from wit_world import exports

import sys

from pbkdf2_compat import install

install()

import pg8000.dbapi

"".encode("idna")


def roundtrip(port: int, user: str, password: str, database: str, text: str) -> None:
    connection = pg8000.dbapi.connect(
        user=user,
        password=password,
        database=database,
        host="127.0.0.1",
        port=port,
        timeout=10,
        ssl_context=False,
    )
    cursor = connection.cursor()
    try:
        cursor.execute(
            "CREATE TEMPORARY TABLE tarawasm_messages ("
            "id BIGSERIAL PRIMARY KEY, body TEXT NOT NULL)"
        )
        cursor.execute(
            "INSERT INTO tarawasm_messages (body) VALUES (%s) RETURNING id",
            (text,),
        )
        inserted_id = cursor.fetchone()[0]
        connection.commit()

        cursor.execute(
            "SELECT body FROM tarawasm_messages WHERE id = %s",
            (inserted_id,),
        )
        received = cursor.fetchone()[0]
        if received != text:
            raise RuntimeError(f"PostgreSQL roundtrip mismatch: {received!r}")
        print(f"PYTHON PG8000 ROUNDTRIP: id={inserted_id} body={received}")
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


class Run(exports.Run):
    def run(self) -> None:
        if len(sys.argv) != 5:
            raise RuntimeError("expected arguments: PORT USER PASSWORD DATABASE MESSAGE")
        roundtrip(int(sys.argv[0]), sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
