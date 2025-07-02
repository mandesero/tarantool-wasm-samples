# wasi:tls source

This compatibility copy comes from WebAssembly/wasi-tls commit
d6fbdc7c6d289fcd6f1b68c0db2c9839eb917100
(v0.2.0-draft+d6fbdc7), matching the tarantool-wasm-rs submodule.

Only the unstable feature annotations were removed. Package names, versions,
resources, functions, and types are unchanged. The current tarawasm all
workflow cannot pass feature flags to its internal WIT validation, while the
actual runtime contract is already explicitly enabled by wasm.so.
