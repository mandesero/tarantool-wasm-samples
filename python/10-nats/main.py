from wit_world import exports

import asyncio
import sys

from ssl_compat import install

install()

import nats

"".encode("idna")


async def roundtrip(
    port: int,
    subject: str,
    request_subject: str,
    text: str,
) -> None:
    client = None
    subscription = None
    responder = None
    try:
        client = await nats.connect(
            servers=[f"nats://127.0.0.1:{port}"],
            connect_timeout=5,
            allow_reconnect=False,
            drain_timeout=5,
        )

        subscription = await client.subscribe(subject)
        await client.flush(timeout=5)
        await client.publish(subject, text.encode("utf-8"))
        await client.flush(timeout=5)
        message = await subscription.next_msg(timeout=10)
        received = message.data.decode("utf-8")
        if received != text:
            raise RuntimeError(f"NATS Pub/Sub mismatch: {received!r}")
        await subscription.unsubscribe()
        subscription = None

        async def echo(message) -> None:
            await message.respond(b"reply:" + message.data)

        responder = await client.subscribe(request_subject, cb=echo)
        await client.flush(timeout=5)
        response = await client.request(
            request_subject,
            text.encode("utf-8"),
            timeout=10,
        )
        reply = response.data.decode("utf-8")
        expected_reply = f"reply:{text}"
        if reply != expected_reply:
            raise RuntimeError(f"NATS request/reply mismatch: {reply!r}")
        await responder.unsubscribe()
        responder = None

        print(f"PYTHON NATS ROUNDTRIP: pubsub={received} request={reply}")
    finally:
        if subscription is not None:
            try:
                await subscription.unsubscribe()
            except Exception:
                pass
        if responder is not None:
            try:
                await responder.unsubscribe()
            except Exception:
                pass
        if client is not None and not client.is_closed:
            try:
                await client.drain()
            finally:
                if not client.is_closed:
                    await client.close()


class Run(exports.Run):
    def run(self) -> None:
        if len(sys.argv) != 4:
            raise RuntimeError(
                "expected arguments: PORT SUBJECT REQUEST_SUBJECT MESSAGE"
            )
        asyncio.run(
            roundtrip(
                int(sys.argv[0]),
                sys.argv[1],
                sys.argv[2],
                sys.argv[3],
            )
        )
