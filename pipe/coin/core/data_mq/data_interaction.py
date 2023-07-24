"""
KAFAK PRODUCE 
"""

from typing import Any
import json

from coin.core.settings.create_log import log
from confluent_kafka import Producer, KafkaException


logging = log()


def produce_sending(topic: Any, message: json) -> None:
    """
    kafka produce
    """
    config: dict[str, str] = {
        "bootstrap.servers": "kafka1:19092, kafka2:29092, kafka3:39092"
    }

    def delivery_report(err, msg) -> None:
        if err is not None:
            logging.info("Message delivery failed : %s", err)
        else:
            logging.info("Message delivered to : %s --> %s", msg.topic(), msg.value())

    produce = Producer(config)
    try:
        produce.produce(
            topic, value=json.dumps(message).encode("utf-8"), callback=delivery_report
        )
    except KafkaException as error:
        logging.error("kafka error : %s ", error)
    finally:
        produce.flush()


async def consume_messages(consumer, topic):
    """
    kafka messageing consumer

    Args:
        consumer (_type_): 컨슈머
        topic (_type_): 받아오는 토픽
    """
    await consumer.start()
    try:
        async for msg in consumer:
            # 메시지 처리 로직 작성
            print(f"Topic: {topic}, Message: {msg.value}")
    finally:
        await consumer.stop()
