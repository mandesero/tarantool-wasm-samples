from wit_world import exports

import asyncio
import sys

from redis.asyncio import Redis

"".encode("idna")


async def receive_message(pubsub, expected: str) -> str:
    async with asyncio.timeout(10):
        while True:
            message = await pubsub.get_message(
                ignore_subscribe_messages=True,
                timeout=1.0,
            )
            if message is None:
                continue
            received = message["data"]
            if received != expected:
                raise RuntimeError(f"Redis Pub/Sub mismatch: {received!r}")
            return received


async def roundtrip(port: int, key: str, channel: str, text: str) -> None:
    client = Redis(
        host="127.0.0.1",
        port=port,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
    )
    pubsub = client.pubsub()
    try:
        async with client.pipeline(transaction=True) as pipeline:
            pipeline.set(key, text)
            pipeline.get(key)
            stored, received = await pipeline.execute()
        if not stored or received != text:
            raise RuntimeError(
                f"Redis pipeline mismatch: stored={stored!r}, value={received!r}"
            )

        await pubsub.subscribe(channel)
        subscribers = await client.publish(channel, text)
        if subscribers != 1:
            raise RuntimeError(
                f"Redis publish expected one subscriber, got {subscribers}"
            )
        event = await receive_message(pubsub, text)
        print(f"PYTHON REDIS ROUNDTRIP: value={received} pubsub={event}")
    finally:
        try:
            try:
                await client.delete(key)
            finally:
                await pubsub.aclose()
        finally:
            await client.aclose()


class Run(exports.Run):
    def run(self) -> None:
        if len(sys.argv) != 4:
            raise RuntimeError("expected arguments: PORT KEY CHANNEL MESSAGE")
        asyncio.run(
            roundtrip(
                int(sys.argv[0]),
                sys.argv[1],
                sys.argv[2],
                sys.argv[3],
            )
        )
