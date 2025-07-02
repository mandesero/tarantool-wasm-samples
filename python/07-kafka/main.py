from wit_world import exports

import asyncio
import sys

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

"".encode("idna")


async def roundtrip(port: int, topic: str, text: str) -> None:
    bootstrap = f"127.0.0.1:{port}"
    producer = AIOKafkaProducer(bootstrap_servers=bootstrap)
    try:
        await producer.start()
        metadata = await producer.send_and_wait(topic, text.encode("utf-8"))
    finally:
        await producer.stop()

    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        group_id=None,
    )
    try:
        await consumer.start()
        async with asyncio.timeout(10):
            record = await consumer.getone()
    finally:
        await consumer.stop()

    received = record.value.decode("utf-8")
    if received != text or record.offset != metadata.offset:
        raise RuntimeError(
            f"Kafka roundtrip mismatch: value={received!r}, "
            f"produced_offset={metadata.offset}, consumed_offset={record.offset}"
        )
    print(f"PYTHON AIOKAFKA ROUNDTRIP: {received}")


class Run(exports.Run):
    def run(self) -> None:
        if len(sys.argv) != 3:
            raise RuntimeError("expected arguments: PORT TOPIC MESSAGE")
        asyncio.run(roundtrip(int(sys.argv[0]), sys.argv[1], sys.argv[2]))
