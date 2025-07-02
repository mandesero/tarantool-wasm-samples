#[allow(warnings)]
mod bindings;

use bindings::exports::wasi::cli::run::Guest as CliGuest;

struct Component;

impl CliGuest for Component {
    fn run() -> Result<(),()> {
        println!("Hello from Rust WASM!");
        Ok(())
    }
}

bindings::export!(Component with_types_in bindings);
