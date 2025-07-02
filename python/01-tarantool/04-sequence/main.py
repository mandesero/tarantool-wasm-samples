from wit_world import exports
from wit_world.imports import say, sequence
from wit_world.imports.tarantool_tarantool_types import Sequence


# ================================
# IncomingHandler stub (no-op)
# ================================

class IncomingHandler(exports.IncomingHandler):
    def handle(self, request, response_out):
        """Stub handler (required by interface)."""
        pass


# ================================
# Test: Tarantool Sequence API
# ================================

def test_sequence():
    say.say_info("PY | ===== Test box sequence start =====", None)

    seq = Sequence(id=1)

    # Try reading current value (should raise an error if not set yet)
    try:
        current = sequence.current(seq)
        say.say_info(f"PY | sequence.current: {current}", None)
    except Exception as e:
        say.say_info(f"PY | sequence.current error: {str(e)}", None)

    # Get next value (should initialize sequence)
    next_val = sequence.next(seq)
    say.say_info(f"PY | sequence.next: {next_val}", None)

    # Check current value again (should now be equal to next_val)
    say.say_info(f"PY | sequence.current: {sequence.current(seq)}", None)

    # Set sequence to a custom value
    sequence.set(seq, 42)
    say.say_info(f"PY | sequence.set: 42", None)
    say.say_info(f"PY | sequence.current: {sequence.current(seq)}", None)

    # Reset sequence (back to undefined)
    sequence.reset(seq)
    say.say_info(f"PY | sequence.reset: done", None)

    # Check current after reset (should raise error)
    try:
        current = sequence.current(seq)
        say.say_info(f"PY | sequence.current after reset: {current}", None)
    except Exception as e:
        say.say_info(f"PY | sequence.current after reset error: {str(e)}", None)

    say.say_info("PY | ===== Test box sequence done =====", None)


# ================================
# WASM entry point
# ================================

class Run(exports.Run):
    def run(self) -> None:
        try:
            test_sequence()
        except Exception as e:
            say.say_error(str(e), None)
