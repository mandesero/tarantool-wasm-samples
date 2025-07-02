import json

from wit_world import exports
from wit_world.imports import box_tuple, key_def, log, msgpack, tuple_format
from wit_world.imports.types import FieldType, KeyPart, KeyPartFlags, LogLevel


def write(level: LogLevel, message: str) -> None:
    log.write(level, message, None)


def encode(value) -> bytes:
    return msgpack.from_json(json.dumps(value))


def decode(value: bytes):
    return json.loads(msgpack.to_json(value))


def test_box_tuple() -> None:
    write(LogLevel.INFO, "PY | ===== Test box tuple start =====")
    default_format = tuple_format.default()
    value = box_tuple.new(encode([1, "abc", {"x": 42}]))
    key_definition = None
    other = None
    updated = None
    upserted = None
    tuple_format.retain(default_format)
    try:
        write(LogLevel.INFO, f"PY | Default format handle: {default_format.handle}")
        write(LogLevel.INFO, f"PY | Created tuple handle: {value.handle}")
        write(LogLevel.INFO, f"PY | field_count = {box_tuple.field_count(value)}")
        write(LogLevel.INFO, f"PY | byte_size = {box_tuple.byte_size(value)}")
        write(LogLevel.INFO, f"PY | to_bytes (decoded) = {decode(box_tuple.to_bytes(value))}")

        value_format = box_tuple.format(value)
        try:
            write(LogLevel.INFO, f"PY | tuple format handle = {value_format.handle}")
        finally:
            tuple_format.release(value_format)

        for position in range(box_tuple.field_count(value)):
            field = box_tuple.field(value, position)
            if field is None:
                raise RuntimeError(f"field[{position}] is missing")
            write(LogLevel.INFO, f"PY | field[{position}] = {decode(field)}")

        path_value = box_tuple.field_by_path(value, "[2].x")
        if path_value is None:
            raise RuntimeError("field_by_path returned none")
        write(LogLevel.INFO, f"PY | field_by_path '[2].x' = {decode(path_value)}")

        updated = box_tuple.update(value, encode([["=", 2, "xyz"]]))
        write(LogLevel.INFO, f"PY | updated tuple = {decode(box_tuple.to_bytes(updated))}")
        upserted = box_tuple.upsert(value, encode([["+", 1, 100]]))
        write(LogLevel.INFO, f"PY | upserted tuple = {decode(box_tuple.to_bytes(upserted))}")
        box_tuple.validate(value, default_format)

        key_definition = key_def.new([
            KeyPart(
                field_no=0,
                field_type=FieldType.UNSIGNED,
                collation=None,
                path=None,
                flags=KeyPartFlags.EXCLUDE_NULL,
            )
        ])
        other = box_tuple.new(encode([1, "abc", {"x": 42}]))
        write(LogLevel.INFO, f"PY | compare(value, other) = {box_tuple.compare(key_definition, value, other)}")
        write(LogLevel.INFO, f"PY | compare_with_key(value, [1]) = {box_tuple.compare_with_key(value, encode([1]), key_definition)}")
    finally:
        if other is not None:
            box_tuple.release(other)
        if key_definition is not None:
            key_def.release(key_definition)
        if upserted is not None:
            box_tuple.release(upserted)
        if updated is not None:
            box_tuple.release(updated)
        box_tuple.release(value)
        tuple_format.release(default_format)
        tuple_format.release(default_format)

    write(LogLevel.INFO, "PY | ===== Test box tuple done =====")


def test_tuple_iterator() -> None:
    write(LogLevel.INFO, "PY | ===== Test box tuple iterator start =====")
    value = box_tuple.new(encode([1, "abc", {"x": 42}]))
    try:
        with box_tuple.Iterator.new(value) as iterator:
            while True:
                field = iterator.next()
                if field is None:
                    break
                write(LogLevel.INFO, f"PY | Iterator pos={iterator.position()}: {decode(field)}")
            iterator.rewind()
            first = iterator.next()
            write(LogLevel.INFO, f"PY | After rewind: {decode(first) if first is not None else None}")
            second = iterator.seek(1)
            write(LogLevel.INFO, f"PY | After seek(1): {decode(second) if second is not None else None}")
    finally:
        box_tuple.release(value)
    write(LogLevel.INFO, "PY | ===== Test box tuple iterator done =====")


class Run(exports.Run):
    def run(self) -> None:
        try:
            test_box_tuple()
            test_tuple_iterator()
        except Exception as exc:
            write(LogLevel.ERROR, str(exc))
            raise
