"""
KAFAK PRODUCE 
"""
from pathlib import Path
from typing import Any
import json

from coin.core.settings.create_log import log
from aiokafka import AIOKafkaProducer

present_path = Path(__file__).parent.parent
logging = log(
    log_location=f"{present_path}/log/kafka_message.log", name="messge_sending"
)


async def produce_sending(topic: Any, message: json):
    """
    kafka produce using aiokafka
    """
    config: dict[str, str] = {
        "bootstrap_servers": "kafka1:19092, kafka2:29092, kafka3:39092"
    }

    producer = AIOKafkaProducer(**config)

    await producer.start()
    if isinstance(message, bytes):
        message = message.decode("utf-8")

    try:
        await producer.send_and_wait(topic, json.dumps(message).encode("utf-8"))
        logging.info(f"Message delivered to: {topic}")
    except Exception as error:
        logging.error(f"kafka error: {error}")
    finally:
        await producer.stop()


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
