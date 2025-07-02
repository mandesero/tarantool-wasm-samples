import { schemaVersion, spaceByName, indexByName, insert, update } from 'tarantool:tarantool/database@0.2.0';
import { fromJson, toJson } from 'tarantool:tarantool/msgpack@0.2.0';
import { write } from 'tarantool:tarantool/log@0.2.0';
import { toBytes, release } from 'tarantool:tarantool/box-tuple@0.2.0';


function log(level, message) {
    write(level, message, undefined);
}


function encode(value) {
    return fromJson(JSON.stringify(value));
}


function decode(value) {
    return JSON.parse(toJson(value));
}


function consumeTuple(tuple) {
    try {
        return decode(toBytes(tuple));
    } finally {
        release(tuple);
    }
}


export const run = {
    run() {
        try {
            log('info', `JS | Schema version: ${schemaVersion()}`);

            const space = spaceByName('test_space');
            if (space === undefined || space === null) {
                throw new Error("space not found: test_space");
            }
            log('info', `JS | Space: ${JSON.stringify(space)}`);

            const primary = indexByName(space, 'primary');
            if (primary === undefined || primary === null) {
                throw new Error("index not found: primary");
            }
            log('info', `JS | Index: ${JSON.stringify(primary)}`);

            const inserted = consumeTuple(insert(space, encode([1, 'bar'])));
            log('info', `JS | Insert successful: ${JSON.stringify(inserted)}`);

            const updated = update(primary, encode([1]), encode([["=", 2, "new_value"]]));
            if (updated === undefined || updated === null) {
                throw new Error("tuple id=1 disappeared before update");
            }
            log('info', `JS | Update successful: ${JSON.stringify(consumeTuple(updated))}`);
        } catch (error) {
            log('error', `JS | Error: ${error instanceof Error ? error.message : JSON.stringify(error)}`);
            throw error;
        }
    },
};
