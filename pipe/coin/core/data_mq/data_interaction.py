"""
KAFAK PRODUCE 
"""

import sys
import json
from typing import Any
from pathlib import Path
from decimal import Decimal
from collections import defaultdict

from aiokafka import AIOKafkaProducer
from aiokafka.errors import NoBrokersAvailable, KafkaProtocolError, KafkaConnectionError

from coin.core.util.create_log import SocketLogCustomer
from coin.core.setting.properties import (
    BOOTSTRAP_SERVER,
    SECURITY_PROTOCOL,
    MAX_BATCH_SIZE,
    MAX_REQUEST_SIZE,
    ARCKS,
)


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


def default(obj: Any):
    if isinstance(obj, Decimal):
        return str(obj)


class KafkaMessageSender:
    """
    3. KafkaMessageSender
        - 카프카 전송 로직
        - 전송 실패 했을 시 우회 로직 완료
    """

    def __init__(self) -> None:
        self.logger = SocketLogCustomer(
            base_path=present_path, file_name="k_log", object_name="kafka"
        )  # 로그 출력을 위한 객체
        self.except_list = defaultdict(list)

    async def produce_sending(
        self,
        message: Any,
        market_name: str,
        symbol: str,
        type_: str = "DataIn",
    ):
        config = {
            "bootstrap_servers": f"{BOOTSTRAP_SERVER}",
            "security_protocol": f"{SECURITY_PROTOCOL}",
            "max_batch_size": int(f"{MAX_BATCH_SIZE}"),
            "max_request_size": int(f"{MAX_REQUEST_SIZE}"),
            "acks": f"{ARCKS}",
            "value_serializer": lambda value: json.dumps(value, default=default).encode(
                "utf-8"
            ),
            "retry_backoff_ms": 100,
        }
        producer = AIOKafkaProducer(**config)

        await producer.start()

        try:
            topic: str = f"{symbol.lower()}{type_}{market_name}"
            await producer.send_and_wait(topic=topic, value=message)
            size: int = deep_getsizeof(message)
            message = f"Message delivered to: {topic} --> counting --> {len(message)} size --> {size}"
            await self.logger.data_log(exchange_name="success", message=message)

            # 불능 상태에서 저장된 메시지가 있는 경우 함께 전송
            while self.except_list[topic]:
                stored_message = self.except_list[topic].pop(0)
                await producer.send_and_wait(topic, stored_message)

        except (NoBrokersAvailable, KafkaProtocolError, KafkaConnectionError) as error:
            error_message = f"Kafka broker error로 인해 임시 저장합니다 : {error}, message: {message}"
            await self.logger.error_log(error_type="error", message=error_message)
            except_list[topic].append(message)
        finally:
            await producer.stop()
