from wit_world import exports
from wit_world.imports import log, sequence
from wit_world.imports.types import LogLevel, Sequence


def write(level: LogLevel, message: str) -> None:
    log.write(level, message, None)


# ================================
# IncomingHandler stub (no-op)
# ================================


# ================================
# Test: Tarantool Sequence API
# ================================

def test_sequence():
    write(LogLevel.INFO, "PY | ===== Test box sequence start =====")

    seq = Sequence(id=1)

    # Try reading current value (should raise an error if not set yet)
    try:
        current = sequence.current(seq)
        write(LogLevel.INFO, f"PY | sequence.current: {current}")
    except Exception as e:
        write(LogLevel.INFO, f"PY | sequence.current error: {str(e)}")

    # Get next value (should initialize sequence)
    next_val = sequence.next(seq)
    write(LogLevel.INFO, f"PY | sequence.next: {next_val}")

    # Check current value again (should now be equal to next_val)
    write(LogLevel.INFO, f"PY | sequence.current: {sequence.current(seq)}")

    # Set sequence to a custom value
    sequence.set(seq, 42)
    write(LogLevel.INFO, "PY | sequence.set: 42")
    write(LogLevel.INFO, f"PY | sequence.current: {sequence.current(seq)}")

    # Reset sequence (back to undefined)
    sequence.reset(seq)
    write(LogLevel.INFO, "PY | sequence.reset: done")

    # Check current after reset (should raise error)
    try:
        current = sequence.current(seq)
        write(LogLevel.INFO, f"PY | sequence.current after reset: {current}")
    except Exception as e:
        write(LogLevel.INFO, f"PY | sequence.current after reset error: {str(e)}")

    write(LogLevel.INFO, "PY | ===== Test box sequence done =====")


# ================================
# WASM entry point
# ================================

class Run(exports.Run):
    def run(self) -> None:
        try:
            test_sequence()
        except Exception as e:
            write(LogLevel.ERROR, str(e))
            raise
