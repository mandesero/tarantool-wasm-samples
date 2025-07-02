from wit_world import exports
from wit_world.imports import say

import code


class Run(exports.Run):
    def run(self) -> None:
        try:
            code.interact(
                banner="Python console running inside a WASI component",
                local={"say": say},
                exitmsg="Leaving WASI Python console",
            )
        except SystemExit:
            pass
