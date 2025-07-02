from wit_world import exports
from wit_world.imports import error, log
from wit_world.imports.types import BoxError, LogContext, LogLevel
from inspect import currentframe


# ================================
# IncomingHandler stub (no-op)
# ================================


# Shortcut for getting current frame (for line number logging)
f = currentframe


def write(level: LogLevel, message: str, context: LogContext | None = None) -> None:
    log.write(level, message, context)


# ================================
# Test: Tarantool error API
# ================================

def test_error():
    write(LogLevel.INFO, "PY | ===== Test box error start =====")

    # Log current file and line where the test starts
    write(LogLevel.INFO, "PY | Running test_error", LogContext(file=f().f_code.co_filename, line=f().f_lineno))

    # Check for any pre-existing error
    last = error.last()
    if last:
        write(LogLevel.INFO, f"PY | Existing error: {error.to_string(last)}")
    else:
        write(LogLevel.INFO, "PY | No existing error found")

    # Create a new error object
    err: BoxError = error.new_with_location(
        0, "from python", f().f_code.co_filename, f().f_lineno
    )
    write(LogLevel.INFO, f"PY | Created error: {error.to_string(err)}")

    # Set the error as the current thread-local error
    error.set(err)
    write(LogLevel.INFO, "PY | Error set")

    # Check that error is now set
    last_after_set = error.last()
    if last_after_set:
        write(LogLevel.INFO, f"PY | Error after set: {error.to_string(last_after_set)}")
    else:
        write(LogLevel.WARNING, "PY | No error found after set() call!")

    # Clear error
    error.clear()

    # Verify that error was cleared
    last = error.last()
    if last:
        write(LogLevel.INFO, f"PY | Existing error: {error.to_string(last)}")
    else:
        write(LogLevel.INFO, "PY | No existing error found")

    write(LogLevel.INFO, "PY | ===== Test box error done =====")


# ================================
# WASM entry point
# ================================

class Run(exports.Run):
    def run(self) -> None:
        try:
            test_error()
        except Exception as e:
            write(LogLevel.ERROR, str(e))
            raise
