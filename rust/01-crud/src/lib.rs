#[allow(warnings)]
mod bindings;

use bindings::exports::wasi::cli::run::Guest as CliGuest;
use bindings::tarantool::tarantool::{box_tuple, database, log, msgpack, types};

struct Component;

fn write(level: types::LogLevel, message: &str) {
    log::write(level, message, None);
}

fn encode(value: serde_json::Value) -> Result<Vec<u8>, types::BoxError> {
    msgpack::from_json(&value.to_string())
}

fn consume_tuple(value: types::BoxTuple) -> Result<String, types::BoxError> {
    let bytes = box_tuple::to_bytes(value);
    box_tuple::release(value);
    msgpack::to_json(&bytes?)
}

impl CliGuest for Component {
    fn run() -> Result<(), ()> {
        if let Err(error) = run_sample() {
            write(types::LogLevel::Error, &format!("RUST | Error: {error:?}"));
            return Err(());
        }
        Ok(())
    }
}

fn run_sample() -> Result<(), types::BoxError> {
    write(
        types::LogLevel::Info,
        &format!("RUST | Schema version: {}", database::schema_version()),
    );

    let space = database::space_by_name("test_space")?
        .expect("space test_space must be created by run.lua");
    write(types::LogLevel::Info, &format!("RUST | Space: {space:?}"));

    let primary = database::index_by_name(space, "primary")?
        .expect("primary index must be created by run.lua");
    write(types::LogLevel::Info, &format!("RUST | Index: {primary:?}"));

    let inserted = database::insert(space, &encode(serde_json::json!([1, "bar"]))?)?;
    write(
        types::LogLevel::Info,
        &format!("RUST | Insert successful: {}", consume_tuple(inserted)?),
    );

    let key = encode(serde_json::json!([1]))?;
    let operations = encode(serde_json::json!([["=", 2, "new_value"]]))?;
    let updated = database::update(primary, &key, &operations)?
        .expect("tuple id=1 disappeared before update");
    write(
        types::LogLevel::Info,
        &format!("RUST | Update successful: {}", consume_tuple(updated)?),
    );
    Ok(())
}

bindings::export!(Component with_types_in bindings);
