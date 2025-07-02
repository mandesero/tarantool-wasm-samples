from wit_world import exports
from wit_world.imports import log, types

import code


class Run(exports.Run):
    def run(self) -> None:
        try:
            code.interact(
                banner="Python console running inside a WASI component",
                local={"log": log, "LogLevel": types.LogLevel},
                exitmsg="Leaving WASI Python console",
            )
        except SystemExit:
            pass
