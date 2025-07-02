from wit_world import exports
from wit_world.imports import key_def, log, tuple_format
from wit_world.imports.types import FieldType, KeyPart, KeyPartFlags, LogLevel


def write(level: LogLevel, message: str) -> None:
    log.write(level, message, None)


def test_tuple_format() -> None:
    write(LogLevel.INFO, "PY | ===== Test box tuple format start =====")
    definition = tuple_format_value = default_format = None
    try:
        definition = key_def.new([
            KeyPart(0, FieldType.UNSIGNED, None, None, KeyPartFlags.IS_NULLABLE),
            KeyPart(1, FieldType.STRING, None, None, KeyPartFlags.EXCLUDE_NULL),
        ])
        tuple_format_value = tuple_format.new([definition])
        write(LogLevel.INFO, f"PY | Created tuple format: {tuple_format_value.handle}")

        tuple_format.retain(tuple_format_value)
        tuple_format.release(tuple_format_value)
        write(LogLevel.INFO, "PY | retain/release pair completed")

        default_format = tuple_format.default()
        write(LogLevel.INFO, f"PY | Default tuple format: {default_format.handle}")
    finally:
        if default_format is not None:
            tuple_format.release(default_format)
        if tuple_format_value is not None:
            tuple_format.release(tuple_format_value)
        if definition is not None:
            key_def.release(definition)

    write(LogLevel.INFO, "PY | ===== Test box tuple format done =====")


class Run(exports.Run):
    def run(self) -> None:
        try:
            test_tuple_format()
        except Exception as exc:
            write(LogLevel.ERROR, str(exc))
            raise
