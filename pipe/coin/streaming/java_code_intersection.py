from typing import Any
import json
import asyncio
from py4j.java_gateway import JavaGateway


gateway = JavaGateway()
kafka_producer = gateway.entry_point.getAsyncKafkaProducer()


async def kafka_topic_java_sending(
    topic: str, message: dict[str, dict[str, Any]]
) -> None:
    encoded_message: bytes = json.dumps(message).encode("utf-8")
    kafka_producer.sendAsync(topic, encoded_message)


async def kafka_sending(topic: str, message: dict[str, dict[str, Any]]) -> None:
    await kafka_topic_java_sending(topic, message)


asyncio.run(kafka_sending())
