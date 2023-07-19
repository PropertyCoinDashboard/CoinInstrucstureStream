from typing import Any

# from setting.create_log import log

from confluent_kafka import Producer, KafkaError, KafkaException
import json

# logging = log()


def produce_sending(topic: Any, message: json) -> None:
    # broker
    config: dict[str, str] = {
        "bootstrap.servers": "kafka1:9092, kafka2:9093, kafka3:9094"
    }

    def delivery_report(err, msg) -> None:
        if err is not None:
            print("Message delivery failed: {}".format(err))
        else:
            print("Message delivered to {} [{}]".format(msg.topic(), msg.partition()))

    produce = Producer(config)

    try:
        produce.produce(
            topic, value=json.dumps(message).encode("utf-8"), callback=delivery_report
        )
    except KafkaException as e:
        print(e)
    finally:
        produce.flush()
