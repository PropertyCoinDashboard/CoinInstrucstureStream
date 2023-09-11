"""
KAFAK PRODUCE 
"""
import json
from typing import Any
from pathlib import Path
from collections import defaultdict

from coin.core.market.util_func import deep_getsizeof
from coin.core.settings.create_log import log
from aiokafka import AIOKafkaProducer
from aiokafka.errors import NoBrokersAvailable, KafkaProtocolError, KafkaConnectionError


present_path = Path(__file__).parent.parent
try:
    logging = log(
        log_location=f"{present_path}/log/kafka_message.log", name="messge_sending"
    )
except (FileNotFoundError, FileExistsError):
    log_path = present_path / "log" / "kafka_message.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)


except_list = defaultdict(list)


async def produce_sending(topic: Any, message: Any):
    config = {
        "bootstrap_servers": "kafka1:19092, kafka2:29092, kafka3:39092",
        "security_protocol": "PLAINTEXT",
        "max_batch_size": 16384,
        "max_request_size": 7000,
        "enable_idempotence": False,
        "acks": "all",
    }
    producer = AIOKafkaProducer(**config)

    await producer.start()

    try:
        encoded_message = json.dumps(message).encode("utf-8")
        await producer.send_and_wait(topic, encoded_message)
        size: int = deep_getsizeof(encoded_message)
        logging.info(
            "Message delivered to: %s --> counting --> %s size --> %s",
            topic,
            len(message),
            size,
        )

        # 불능 상태에서 저장된 메시지가 있는 경우 함께 전송
        while except_list[topic]:
            stored_message = except_list[topic].pop(0)
            await producer.send_and_wait(topic, stored_message)

    except (
        NoBrokersAvailable,
        KafkaProtocolError,
        KafkaConnectionError,
    ) as error:
        logging.error(
            "Kafka broker error로 인해 임시 저장합니다 : %s, message: %s", error, message
        )
        except_list[topic].append(json.dumps(message).encode("utf-8"))
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
