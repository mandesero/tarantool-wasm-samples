from wit_world import exports

import asyncio
import sys
from grpclib.server import Server

from helloworld_grpc import GreeterBase
from helloworld_pb2 import HelloReply

"".encode("idna")


class Greeter(GreeterBase):
    async def SayHello(self, stream):
        request = await stream.recv_message()
        await stream.send_message(HelloReply(message=f"Hello, {request.name}!"))


async def serve(port: int) -> None:
    server = Server([Greeter()])
    await server.start("127.0.0.1", port)
    print(f"READY 127.0.0.1:{port}", flush=True)
    try:
        await server.wait_closed()
    finally:
        server.close()
        await server.wait_closed()


class Run(exports.Run):
    def run(self) -> None:
        asyncio.run(serve(int(sys.argv[0]) if sys.argv else 50051))
