from wit_world import exports
from wit_world.imports import say, key_def, tuple_format
from wit_world.imports.tarantool_tarantool_types import KeyPart, KeyPartFlags


# ================================
# IncomingHandler stub (no-op)
# ================================

class IncomingHandler(exports.IncomingHandler):
    def handle(self, request, response_out):
        """Stub handler (required by interface)."""
        pass


# ================================
# Test: TupleFormat API
# ================================

def test_tuple_format():
    say.say_info("PY | ===== Test box tuple format start =====", None)

    # Define key parts
    parts = [
        KeyPart(
            field_no=0,
            field_type="unsigned",
            collation=None,
            path=None,
            flags=KeyPartFlags.IS_NULLABLE
        ),
        KeyPart(
            field_no=1,
            field_type="string",
            collation=None,
            path=None,
            flags=KeyPartFlags.EXCLUDE_NULL
        ),
    ]

    # Create key_def from parts
    kd = key_def.new(parts)
    say.say_info(f"PY | Created key_def: {kd}", None)

    # Create a new tuple_format using the key_def
    tf = tuple_format.new([kd])
    say.say_info(f"PY | Created tuple_format: {tf}", None)

    # Increase reference count
    tuple_format.ref(tf)
    say.say_info("PY | Called tuple_format.ref", None)

    # Decrease reference count
    tuple_format.unref(tf)
    say.say_info("PY | Called tuple_format.unref", None)

    # Get default tuple_format
    default_tf = tuple_format.default()
    say.say_info(f"PY | Default tuple_format: {default_tf}", None)

    say.say_info("PY | ===== Test box tuple format done =====", None)


# ================================
# WASM entry point
# ================================

class Run(exports.Run):
    def run(self) -> None:
        try:
            test_tuple_format()
        except Exception as e:
            say.say_error(str(e), None)
