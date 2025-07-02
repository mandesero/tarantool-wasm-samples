# Interactive Python console

Runs Python's `InteractiveConsole` inside the guest component. Standard input is
inherited from the Tarantool process, so expressions are evaluated interactively;
the current Tarantool `say` WIT import is also exposed as `say`.

Complete the [root setup](https://github.com/mandesero/tarantool-wasm-samples),
then build and start the console from an interactive terminal:

```sh
make build SAMPLE=python/06-cli
make run SAMPLE=python/06-cli
```

Example session:

```pycon
Python console running inside a WASI component
>>> 1 + 2
3
>>> log.write(LogLevel.INFO, "From the Python console", None)
>>> exit()
Leaving WASI Python console
```

The Tarantool log contains `From the Python console`. Press Ctrl-D as an
alternative to `exit()`.

For a deterministic non-interactive check, commands can be piped to the same
entrypoint:

```sh
printf 'print("CLI:", 1 + 2)\n' | make run SAMPLE=python/06-cli
```

`run.lua` enables only inherited stdin; environment and network inheritance
remain disabled, and the shared memory/fuel limits still apply. The host uses
