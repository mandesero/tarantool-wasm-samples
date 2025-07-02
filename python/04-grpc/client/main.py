from wit_world import exports

import asyncio
import sys
from grpclib.client import Channel

from helloworld_pb2 import HelloRequest
from helloworld_grpc import GreeterStub

"".encode("idna")


async def request(port: int) -> None:
    async with Channel("127.0.0.1", port) as channel:
        reply = await GreeterStub(channel).SayHello(HelloRequest(name="Alice"))
        if reply.message != "Hello, Alice!":
            raise RuntimeError(f"unexpected reply: {reply.message}")
        print("GRPC RESPONSE: " + reply.message)


class Run(exports.Run):
    def run(self) -> None:
        asyncio.run(request(int(sys.argv[0]) if sys.argv else 50051))
