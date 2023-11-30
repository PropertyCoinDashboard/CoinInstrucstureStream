import asyncio
from aiokafka import AIOKafkaConsumer
from coin.core.data_mq.data_interaction import consume_messages
from coin.core.config.properties import (
    BTC_AVERAGE_TOPIC_NAME,
    ETH_AVERAGE_TOPIC_NAME,
    UPBIT_BTC_REAL_TOPIC_NAME,
    BITHUMB_BTC_REAL_TOPIC_NAME,
    KORBIT_BTC_REAL_TOPIC_NAME,
)


async def kafka_consumer_concurrency():
    consumers = []
    for topic in [
        UPBIT_BTC_REAL_TOPIC_NAME,
        BITHUMB_BTC_REAL_TOPIC_NAME,
        KORBIT_BTC_REAL_TOPIC_NAME,
    ]:
        consumer = AIOKafkaConsumer(
            topic,
            bootstrap_servers=["kafka1:19091", "kafka2:29092", "kafka3:39093"],
            auto_offset_reset="earliest",
            value_deserializer=lambda m: m.decode("utf-8"),
        )
        consumers.append(consume_messages(consumer, topic))
    await asyncio.gather(*consumers)


if __name__ == "__main__":
    asyncio.run(kafka_consumer_concurrency())
