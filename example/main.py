from wit_world import VArg, Responce, VArg_Number, VArg_Name, VResponce_Num, VResponce_Str, VResponce_None_

import asyncio
from grpclib.client import Channel

from example_pb2 import HelloRequest, NumberRequest
from example_grpc import GreeterStub


async def say_hello(address: str, name: str) -> Responce:
    host, port = address.split(":")
    async with Channel(host, int(port)) as channel:
        stub = GreeterStub(channel)
        reply = await stub.SayHello(HelloRequest(name=name))
        return Responce(status="OK", value=VResponce_Str(reply.message), error="")


async def process_number(address: str, number: int) -> Responce:
    host, port = address.split(":")
    async with Channel(host, int(port)) as channel:
        stub = GreeterStub(channel)
        reply = await stub.ProcessNumber(NumberRequest(value=number))
        return Responce(status="OK", value=VResponce_Num(reply.result), error="")


class WitWorld:
    def call(self, address: str, service: str, method: str, args: VArg) -> Responce:
        try:
            if service != "example.Greeter":
                return Responce(status="Error", value=VResponce_None_(), error=f"Unsupported service: {service}")

            if isinstance(args, VArg_Name) and method == "SayHello":
                return asyncio.run(say_hello(address, args.value))

            if isinstance(args, VArg_Number) and method == "ProcessNumber":
                return asyncio.run(process_number(address, args.value))

            return Responce(status="Error", value=VResponce_None_(), error=f"Unsupported method {method} for argument type {type(args).__name__}")

        except Exception as e:
            return Responce(status="Error", value=VResponce_None_(), error=f"gRPC call failed: {e}")
