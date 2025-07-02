from wit_world import exports
from wit_world.imports import say, tarantool_tarantool_error as error, key_def, msgpack, box_tuple, tuple_format
from wit_world.imports.tarantool_tarantool_types import BoxError, KeyPart, KeyPartFlags
import json


# ================================
# IncomingHandler stub (required by interface)
# ================================

class IncomingHandler(exports.IncomingHandler):
    def handle(self, request, response_out):
        """Stub IncomingHandler, does nothing for now."""
        pass


# ================================
# Utility functions for encoding/decoding
# ================================

def encode(obj):
    """Serialize Python object → JSON → MsgPack → bytes."""
    try:
        return msgpack.encode(json.dumps(obj).encode('utf-8'))
    except Exception as error:
        say.say_error(f"PY | Error in encode: {json.dumps({'error': str(error)}, indent=2)}", None)
        raise


def decode(*, data=None, ptr=None):
    """Decode MsgPack → JSON → Python object."""
    try:
        if ptr:
            decoded_json_bytes: bytes = msgpack.decode_from_raw_ptr(ptr)
        elif data:
            decoded_json_bytes: bytes = msgpack.decode(data)
        else:
            raise ValueError("Either 'data' or 'ptr' must be provided")

        return json.loads(decoded_json_bytes.decode('utf-8'))
    except Exception as error:
        say.say_error(f"PY | Error in decode: {json.dumps({'error': str(error)}, indent=2)}", None)
        raise


# ================================
# Test: Box Tuple API
# ================================

def test_box_tuple():
    say.say_info("PY | ===== Test box tuple start =====", None)

    # Get default tuple format pointer
    tf = tuple_format.default()
    say.say_info(f"PY | Default format (ptr): {hex(tf)}", None)

    # Create a new tuple
    data = encode([1, "abc", {"x": 42}])
    tup = box_tuple.new(data)
    say.say_info(f"PY | Created tuple [1, 'abc', {{'x': 42}}], ptr={hex(tup)}", None)

    # Increment tuple reference count
    rc = box_tuple.ref(tup)
    say.say_info(f"PY | tuple.ref() => {rc}", None)

    # Field count and tuple size
    fc = box_tuple.field_count(tup)
    say.say_info(f"PY | field_count = {fc}", None)

    size = box_tuple.bsize(tup)
    say.say_info(f"PY | bsize = {size}", None)

    # Dump tuple to buffer and decode
    buf = box_tuple.to_buf(tup)
    say.say_info(f"PY | to_buf (decoded) = {decode(data=buf)}", None)

    # Get tuple format
    tf2 = box_tuple.format(tup)
    say.say_info(f"PY | format (ptr) = {hex(tf2)}", None)

    # Access fields by index
    for i in range(fc):
        field = box_tuple.field(tup, i)
        if isinstance(field, int):
            say.say_info(f"PY | field[{i}] = {decode(ptr=field)}", None)
        else:
            say.say_info(f"PY | field[{i}] error: {field}", None)

    # Access field by JSON path
    path_result = box_tuple.field_by_path(tup, "[3].x", 1)
    if isinstance(path_result, int):
        say.say_info(f"PY | field_by_path \"[3].x\" = {decode(ptr=path_result)}", None)
    else:
        say.say_info(f"PY | field_by_path error: {path_result}", None)

    # Update tuple
    update_expr = encode([["=", 1, "xyz"]])
    updated = box_tuple.update(tup, update_expr)
    updated_val = decode(data=box_tuple.to_buf(updated))
    say.say_info(f"PY | updated tuple (set field 1 to 'xyz') = {updated_val}", None)

    # Upsert tuple
    upsert_expr = encode([["+", 1, 100]])
    upserted = box_tuple.upsert(tup, upsert_expr)
    upserted_val = decode(data=box_tuple.to_buf(upserted))
    say.say_info(f"PY | upserted tuple (increment field 1 by 100) = {upserted_val}", None)

    # Validate tuple against format
    valid = box_tuple.validate(tup, tf)
    say.say_info(f"PY | validate = {valid}", None)

    # Create key_def for comparisons
    key_parts = [
        KeyPart(
            field_no=0,
            field_type="unsigned",
            collation=None,
            path=None,
            flags=KeyPartFlags.EXCLUDE_NULL
        )
    ]
    kd = key_def.new(key_parts)
    say.say_info(f"PY | Created key_def: {kd}", None)

    # Compare with another tuple
    another_data = encode([1, "abc", {"x": 42}])
    other = box_tuple.new(another_data)
    cmp_result = box_tuple.compare(kd, tup, other)
    say.say_info(f"PY | compare(tup, other) = {cmp_result}", None)

    # Compare with key
    key = encode([1])
    cmp_key_result = box_tuple.compare_with_key(tup, key, kd)
    say.say_info(f"PY | compare_with_key(tup, [1]) = {cmp_key_result}", None)

    # Unref the tuple
    box_tuple.unref(tup)
    say.say_info("PY | tuple.unref() done", None)

    say.say_info("PY | ===== Test box tuple done =====", None)


# ================================
# Test: Tuple Iterator API
# ================================

def test_tuple_iterator():
    say.say_info("PY | ===== Test box tuple iterator start =====", None)

    # Create tuple
    data = encode([1, "abc", {"x": 42}])
    tup = box_tuple.new(data)
    say.say_info(f"PY | Created tuple [1, 'abc', {{'x': 42}}], ptr={hex(tup)}", None)

    # Create iterator for the tuple
    titer = box_tuple.TupleIterator.new_tuple_iterator(tup)
    say.say_info("PY | Created tuple iterator", None)

    # Iterate through all fields
    while True:
        field = titer.next()
        if not field:
            break
        say.say_info(f"PY | Iterator pos={titer.position()}: {decode(ptr=field)}", None)

    # Report final position
    pos = titer.position()
    say.say_info(f"PY | Position after iteration: {pos}", None)

    # Rewind and test again
    titer.rewind()
    say.say_info("PY | Rewound iterator", None)

    field = titer.next()
    say.say_info(f"PY | After rewind, next field (pos={titer.position()}): {decode(ptr=field)}", None)

    # Seek and continue
    titer.seek(1)
    say.say_info(f"PY | After seek(1), pos={titer.position()}", None)

    field = titer.next()
    say.say_info(f"PY | Field after seek: {decode(ptr=field)}", None)

    say.say_info("PY | ===== Test box tuple iterator done =====", None)


# ================================
# WASM entry point
# ================================

class Run(exports.Run):
    def run(self) -> None:
        try:
            test_box_tuple()
            test_tuple_iterator()
        except Exception as e:
            say.say_error(str(e), None)
