import asyncio
from grpclib.server import Server
from grpclib.utils import graceful_exit

from example_pb2 import HelloReply, NumberReply
from example_grpc import GreeterBase


class Greeter(GreeterBase):

    async def SayHello(self, stream):
        request = await stream.recv_message()
        name = request.name
        print(f"Received SayHello request: name={name}")
        await stream.send_message(
            HelloReply(message=f'Hello, {name}!')
        )

    async def ProcessNumber(self, stream):
        request = await stream.recv_message()
        value = request.value
        print(f"Received ProcessNumber request: value={value}")
        result = value * 2
        await stream.send_message(
            NumberReply(result=result)
        )


async def main():
    server = Server([Greeter()])
    with graceful_exit([server]):
        await server.start('127.0.0.1', 50051)
        print('Serving on 127.0.0.1:50051')
        await server.wait_closed()


if __name__ == '__main__':
    asyncio.run(main())
