import json

from wit_world import exports
from wit_world.imports import box_tuple, database, index as index_api, log, msgpack, transaction
from wit_world.imports.types import BoxTuple, Index, IteratorType, LogLevel, Space


def write(level: LogLevel, message: str) -> None:
    log.write(level, message, None)


def encode(value) -> bytes:
    return msgpack.from_json(json.dumps(value))


def decode(data: bytes):
    return json.loads(msgpack.to_json(data))


def consume_tuple(value: BoxTuple):
    try:
        return decode(box_tuple.to_bytes(value))
    finally:
        box_tuple.release(value)


def require_space(name: str) -> Space:
    space = database.space_by_name(name)
    if space is None:
        raise RuntimeError(f"space not found: {name}")
    return space


def require_index(space: Space, name: str) -> Index:
    index = database.index_by_name(space, name)
    if index is None:
        raise RuntimeError(f"index not found: {name}")
    return index


def test_box() -> None:
    write(LogLevel.INFO, "PY | ===== Test box API start =====")
    write(LogLevel.INFO, f"PY | Schema version: {database.schema_version()}")

    space = require_space("test_space")
    primary = require_index(space, "primary")
    write(LogLevel.INFO, f"PY | Space: id={space.id}")
    write(LogLevel.INFO, f"PY | Index: space_id={primary.space_id}, id={primary.id}")

    rows = [
        [1, "Alice", 25],
        [2, "Bob", 30],
        [3, "Charlie", 35],
        [4, "David", 40],
        [5, "Eve", 4],
    ]

    for row in rows[:2]:
        inserted = consume_tuple(database.insert(space, encode(row)))
        write(LogLevel.INFO, f"PY | Inserted: {row}, decoded={inserted}")

    transaction.begin()
    try:
        for row in rows[2:]:
            inserted = consume_tuple(database.insert(space, encode(row)))
            write(LogLevel.INFO, f"PY | Inserted: {row}, decoded={inserted}")
        transaction.commit()
    except Exception:
        transaction.rollback()
        raise

    updated = database.update(primary, encode([1]), encode([["=", 3, 26]]))
    if updated is None:
        raise RuntimeError("tuple id=1 disappeared before update")
    write(LogLevel.INFO, f"PY | Updated id=1 (age=26), decoded={consume_tuple(updated)}")

    replaced = consume_tuple(database.replace(space, encode([2, "Bob Jr.", 31])))
    write(LogLevel.INFO, f"PY | Replaced id=2 -> ['Bob Jr.', 31], decoded={replaced}")

    database.upsert(primary, encode([6, "Frank", 50]), encode([["+", 3, 1]]))
    database.upsert(primary, encode([1, "Alice", 0]), encode([["+", 3, 1]]))
    write(LogLevel.INFO, "PY | Upserts completed")

    deleted = database.delete(primary, encode([3]))
    if deleted is None:
        raise RuntimeError("tuple id=3 disappeared before delete")
    write(LogLevel.INFO, f"PY | Deleted id=3, decoded={consume_tuple(deleted)}")

    write(LogLevel.INFO, "PY | Iterating over space content:")
    with index_api.Iterator.new(primary, IteratorType.ALL, encode([])) as iterator:
        while True:
            item = iterator.next()
            if item is None:
                break
            write(LogLevel.INFO, f"PY |\tTuple: {consume_tuple(item)}")

    database.truncate(space)
    write(LogLevel.INFO, "PY | Truncated space")
    write(LogLevel.INFO, "PY | ===== Test box API done =====")


class Run(exports.Run):
    def run(self) -> None:
        try:
            test_box()
        except Exception as exc:
            write(LogLevel.ERROR, str(exc))
            raise
