"""
KAFAK PRODUCE 
"""

from typing import Any
import json

# from setting.create_log import log
from confluent_kafka import Producer, KafkaException


# logging = log()
def produce_sending(topic: Any, message: json) -> None:
    """
    kafka produce
    """
    config: dict[str, str] = {
        "bootstrap.servers": "kafka1:19092, kafka2:29092, kafka3:39092"
    }

    def delivery_report(err, msg) -> None:
        if err is not None:
            print(f"Message delivery failed: {err}")
        else:
            print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

    produce = Producer(config)

    try:
        produce.produce(
            topic, value=json.dumps(message).encode("utf-8"), callback=delivery_report
        )
    except KafkaException as error:
        print("kafka error : %s ", error)
    finally:
        produce.flush()
