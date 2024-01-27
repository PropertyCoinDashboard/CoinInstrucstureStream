"""
KAFAK PRODUCE 
"""
import sys
import json
from typing import Any
from pathlib import Path
from collections import defaultdict

from coin.core.util.create_log import log, SocketLogCustomer
from aiokafka import AIOKafkaProducer
from aiokafka.errors import NoBrokersAvailable, KafkaProtocolError, KafkaConnectionError


present_path = Path(__file__).parent
except_list: defaultdict[Any, list] = defaultdict(list)


# 메모리 계산
def deep_getsizeof(obj, seen=None) -> int:
    """재귀적으로 객체의 메모리 사용량을 계산하는 함수"""
    if seen is None:
        seen = set()

    obj_id = id(obj)
    if obj_id in seen:
        return 0

    # 이미 본 객체는 저장
    seen.add(obj_id)

    size = sys.getsizeof(obj)

    if isinstance(obj, dict):
        size += sum(deep_getsizeof(v, seen) for v in obj.values())
        size += sum(deep_getsizeof(k, seen) for k in obj.keys())
    elif hasattr(obj, "__iter__") and not isinstance(obj, (str, bytes, bytearray)):
        size += sum(deep_getsizeof(i, seen) for i in obj)

    return size


async def consume_messages(consumer, topic) -> None:
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


class KafkaMessageSender:
    """
    3. KafkaMessageSender
        - 카프카 전송 로직
        - 전송 실패 했을 시 우회 로직 완료
    """

    def __init__(self) -> None:
        self.p = SocketLogCustomer(
            base_path=Path(__file__).parent, file_name="mq_logging", object_name="kafka"
        )  # 로그 출력을 위한 객체
        self.except_list = defaultdict(list)

    async def produce_sending(self, topic: Any, message: Any):
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
            message: str = f"Message delivered to: {topic} --> counting --> {len(message)} size --> {size}"
            self.p.data_log(exchange_name="success", message=message)

            # 불능 상태에서 저장된 메시지가 있는 경우 함께 전송
            while except_list[topic]:
                stored_message = except_list[topic].pop(0)
                await producer.send_and_wait(topic, stored_message)

        except (
            NoBrokersAvailable,
            KafkaProtocolError,
            KafkaConnectionError,
        ) as error:
            error_message: str = (
                f"Kafka broker error로 인해 임시 저장합니다 : {error}, message: {message}"
            )
            self.p.error_log(error_type="error", message=error_message)
            except_list[topic].append(json.dumps(message).encode("utf-8"))
        finally:
            await producer.stop()

    async def message_kafka_sending(
        self, data: Any, market_name: str, symbol: str, type_: str = "DataIn"
    ) -> None:
        """카프카 전송 우회 로직 작성

        Args:
            data (Any):  데이터
            market_name (str): 마켓이름
            symbol (str): 코인심볼
        """
        try:
            await self.produce_sending(
                topic=f"{symbol.lower()}{type_}{market_name}",
                message=data,
            )
            # 불능 상태에서 저장된 메시지가 있는 경우 함께 전송
            while self.except_list[market_name]:
                stored_message = self.except_list[market_name].pop(0)
                await self.produce_sending(
                    topic=f"{type_}{market_name}",
                    message=stored_message,
                )

        except KafkaConnectionError as error:
            await self.p.error_log(
                error_type="etc_error",
                message=f"broker 통신 불가로 임시 저장합니다 --> {error} data -> {len(self.except_list)}",
            )
            self.except_list[market_name].append(data)
