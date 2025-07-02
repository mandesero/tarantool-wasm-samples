import json

from wit_world import exports
from wit_world.imports import key_def, log, msgpack
from wit_world.imports.types import Collation, FieldType, KeyPart, KeyPartFlags, LogLevel


def write(level: LogLevel, message: str) -> None:
    log.write(level, message, None)


def encode(value) -> bytes:
    return msgpack.from_json(json.dumps(value))


def test_key_def() -> None:
    write(LogLevel.INFO, "PY | ===== Test box key-def start =====")
    left = right = duplicate = merged = None
    try:
        left = key_def.new([
            KeyPart(0, FieldType.UNSIGNED, None, None, KeyPartFlags.IS_NULLABLE),
            KeyPart(3, FieldType.STRING, Collation.UNICODE, "t1", KeyPartFlags.EXCLUDE_NULL),
        ])
        right = key_def.new([
            KeyPart(1, FieldType.STRING, None, None, KeyPartFlags.EXCLUDE_NULL)
        ])

        for name, value in (("left", left), ("right", right)):
            write(LogLevel.INFO, f"PY | {name} handle={value.handle}")
            write(LogLevel.INFO, f"PY | {name} parts={key_def.dump_parts(value)}")
            write(LogLevel.INFO, f"PY | {name} part count={key_def.part_count(value)}")

        duplicate = key_def.duplicate(left)
        merged = key_def.merge(left, right)
        write(LogLevel.INFO, f"PY | duplicate parts={key_def.dump_parts(duplicate)}")
        write(LogLevel.INFO, f"PY | merged parts={key_def.dump_parts(merged)}")

        key_def.validate_key(left, encode([1]))
        write(LogLevel.INFO, "PY | validate_key([1]) succeeded")
        key_def.validate_full_key(left, encode([1, "abc"]))
        write(LogLevel.INFO, "PY | validate_full_key([1, 'abc']) succeeded")
        try:
            key_def.validate_key(left, encode(["xxx"]))
        except Exception as exc:
            write(LogLevel.INFO, f"PY | invalid key rejected: {exc}")
    finally:
        for value in (merged, duplicate, right, left):
            if value is not None:
                key_def.release(value)

    write(LogLevel.INFO, "PY | ===== Test box key-def done =====")


class Run(exports.Run):
    def run(self) -> None:
        try:
            test_key_def()
        except Exception as exc:
            write(LogLevel.ERROR, str(exc))
            raise
