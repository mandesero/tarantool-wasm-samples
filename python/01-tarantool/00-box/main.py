from wit_world import exports
from wit_world.imports import say, msgpack, txn
from wit_world.imports import box_tuple
from wit_world.imports import ttbox as box
from wit_world.imports.tarantool_tarantool_types import Space, Index, Iterator, IteratorType
import json


# ================================
# Utility functions for encoding/decoding
# ================================

def encode(obj):
    """Serialize a Python object → JSON → MsgPack → bytes (for Tarantool tuple insertion)."""
    try:
        return msgpack.encode(json.dumps(obj).encode('utf-8'))
    except Exception as error:
        say.say_error(f"PY | Error in encode: {json.dumps({'error': str(error)}, indent=2)}", None)
        raise


def decode(*, data=None, ptr=None):
    """Decode MsgPack bytes → JSON string → Python object.
    Supports two modes:
    - data: raw MsgPack buffer
    - ptr: Tarantool tuple pointer (decoded via box_tuple API)
    """
    try:
        if ptr:
            decoded_json_bytes: bytes = msgpack.decode_from_raw_ptr(ptr)
        elif data:
            decoded_json_bytes: bytes = msgpack.decode(data)
        else:
            raise ValueError("Either 'data' or 'ptr' must be provided for decode()")

        decoded_json_string = decoded_json_bytes.decode('utf-8')
        return json.loads(decoded_json_string)
    except Exception as error:
        say.say_error(f"PY | Error in decode: {json.dumps({'error': str(error)}, indent=2)}", None)
        raise


# ================================
# Main box API testing
# ================================

def test_box():
    say.say_info(f"PY | ===== Test box API start =====", None)

    # Get current Tarantool schema version
    schema_ver = box.schema_version()
    say.say_info(f"PY | Schema version: {schema_ver}", None)

    # Lookup space by name
    space: Space = box.space_by_name("test_space")
    say.say_info(f"PY | Space: id={space.id}", None)

    # Lookup index by name
    index: Index = box.index_by_name(space, "primary")
    say.say_info(f"PY | Index: space_id={index.space_id}, id={index.id}, index_base={index.index_base}", None)

    # Example test data (id, name, age)
    test_data = [
        [1, "Alice", 25],
        [2, "Bob", 30],
        [3, "Charlie", 35],
        [4, "David", 40],
        [5, "Eve", 4],
    ]

    # Insert first two rows without transaction
    for row in test_data[:2]:
        tup_bytes = encode(row)
        inserted = box.insert(space, tup_bytes)
        say.say_info(f"PY | Inserted: {row}, tuple_ptr={hex(inserted)}, decoded={decode(data=box_tuple.to_buf(inserted))}", None)

    # Insert remaining rows inside a transaction
    txn.begin()
    for row in test_data[2:]:
        tup_bytes = encode(row)
        inserted = box.insert(space, tup_bytes)
        say.say_info(f"PY | Inserted: {row}, tuple_ptr={hex(inserted)}, decoded={decode(data=box_tuple.to_buf(inserted))}", None)
    txn.commit()

    # Update: change age for id=1 to 26
    key = encode([1])
    ops = encode([["=", 2, 26]])  # Set field at index 2 (age) to 26
    updated = box.update(index, key, ops)
    say.say_info(f"PY | Updated id=1 (age=26), tuple_ptr={hex(updated)}, decoded={decode(data=box_tuple.to_buf(updated))}", None)

    # Replace: completely replace tuple for id=2
    replaced = box.replace(space, encode([2, "Bob Jr.", 31]))
    say.say_info(f"PY | Replaced id=2 -> ['Bob Jr.', 31], tuple_ptr={hex(replaced)}, decoded={decode(data=box_tuple.to_buf(replaced))}", None)

    # Upsert: id=6 does not exist → insert
    upsert_tuple = encode([6, "Frank", 50])
    upsert_ops = encode([["+", 2, 1]])  # Increase age if exists
    box.upsert(index, upsert_tuple, upsert_ops)
    say.say_info(f"PY | Upserted id=6 (inserted new)", None)

    # Upsert: id=1 exists → increment age by 1
    box.upsert(index, encode([1, "Alice", 0]), encode([["+", 2, 1]]))
    say.say_info(f"PY | Upserted id=1 (age incremented)", None)

    # Delete: remove tuple with id=3
    deleted = box.delete(index, encode([3]))
    say.say_info(f"PY | Deleted id=3, tuple_ptr={hex(deleted)}, decoded={decode(data=box_tuple.to_buf(deleted))}", None)

    # Iterate over all remaining tuples in the space
    say.say_info("PY | Iterating over space content:", None)
    iterator = Iterator.new_iterator(index, IteratorType.ITER_ALL, encode([]))
    while True:
        try:
            tup = iterator.next()
            say.say_info(f"PY |\tTuple: {decode(data=box_tuple.to_buf(tup))}", None)
        except Exception:
            # End of iteration (StopIteration or similar)
            break

    # Truncate: clear all data in space
    box.truncate(space)
    say.say_info("PY | Truncated space", None)

    say.say_info(f"PY | ===== Test box API done =====", None)


# ================================
# Incoming request handler stub
# ================================

class IncomingHandler(exports.IncomingHandler):
    def handle(self, request, response_out):
        """No-op (stub) IncomingHandler implementation."""
        pass


# ================================
# WASM entry point
# ================================

class Run(exports.Run):
    def run(self) -> None:
        try:
            test_box()
        except Exception as e:
            say.say_error(str(e), None)
