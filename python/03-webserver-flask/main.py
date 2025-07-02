from wit_world import exports
from wit_world.imports import say, ttbox as box, msgpack, box_tuple
from wit_world.imports.tarantool_tarantool_types import *
from inspect import currentframe
import time
import json
import sys

# Patch zlib for componentize-py WASM runtime
import __zlib
sys.modules["zlib"] = __zlib

# Patch importlib.metadata.version to avoid runtime errors
import importlib.metadata
importlib.metadata.version = lambda _: ""

# Ensure idna encoding is pre-loaded for WASM
"".encode('idna')

# ================================
# Flask Web API setup
# ================================

from flask import Flask, request, jsonify

app = Flask(__name__)
f = currentframe


# ================================
# Utility functions
# ================================

def encode(obj):
    """Serialize Python object → JSON → MsgPack → bytes."""
    try:
        return msgpack.encode(json.dumps(obj).encode('utf-8'))
    except Exception as error:
        say.say_error(f"PY | Error in encode: {json.dumps({'error': str(error)}, indent=2)}")
        raise


def decode(*, data=None, ptr=None):
    """Decode MsgPack → JSON → Python object."""
    try:
        if ptr:
            decoded_json_bytes: bytes = msgpack.decode_from_raw_ptr(ptr)
        elif data:
            decoded_json_bytes: bytes = msgpack.decode(data)
        else:
            raise ValueError("Either 'data' or 'ptr' must be provided for decode()")

        return json.loads(decoded_json_bytes.decode('utf-8'))
    except Exception as error:
        say.say_error(f"PY | Error in decode: {json.dumps({'error': str(error)}, indent=2)}")
        raise


# ================================
# Flask Routes
# ================================

@app.route("/")
def hello():
    return "Hello from WASM!"


@app.route('/time')
def time_handler():
    """Return server time as JSON."""
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    return jsonify({"time": current_time})


@app.route('/insert/<space>/<tup>')
def insert_tuple(space, tup: str):
    """Insert a tuple into the given space.

    Example call:
    GET /insert/test_space/1,Alice,25
    """
    try:
        space_obj: Space = box.space_by_name(space)

        tuple_data = [int(x) if x.isdigit() else x for x in tup.split(',')]
        say.say_info(
            f"PY | Try to insert {tuple_data} to space {space_obj}",
            LogContext(filename=f().f_code.co_filename, line=f().f_lineno)
        )
        inserted = box.insert(space_obj, encode(tuple_data))

        return jsonify({"message": f"Inserted, tuple_ptr = {hex(inserted)[2:]}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/content/<space>')
def content(space):
    """List all tuples in the given space (iterate over primary index)."""
    try:
        say.say_info(
            f"PY | Get space content - space '{space}'",
            LogContext(filename=f().f_code.co_filename, line=f().f_lineno)
        )
        space_obj: Space = box.space_by_name(space)
        index_obj: Index = box.index_by_name(space_obj, "primary")
        
        t = Iterator.new_iterator(index_obj, IteratorType.ITER_ALL, encode([]))
        tuples = []
        while True:
            try:
                tup = t.next()
                tuples.append(decode(data=box_tuple.to_buf(tup)))
            except:
                break

        return jsonify({"space": space, "tuples": tuples})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ================================
# IncomingHandler stub (no-op)
# ================================

class IncomingHandler(exports.IncomingHandler):
    def handle(self, request, response_out):
        """Stub handler (required by interface)."""
        pass


# ================================
# WASM entry point
# ================================

class Run(exports.Run):
    def run(self) -> None:
        try:
            app.run(debug=False, threaded=False)
        except Exception as e:
            say.say_error(str(e), None)
