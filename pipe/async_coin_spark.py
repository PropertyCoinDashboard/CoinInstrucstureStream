"""
spark 
"""
from concurrent.futures import ThreadPoolExecutor
from connection.streaming_connection import run_spark_streaming
from coin.core.config.properties import (
    BTC_TOPIC_NAME,
    ETH_TOPIC_NAME,
    BTC_AVERAGE_TOPIC_NAME,
    ETH_AVERAGE_TOPIC_NAME,
)


def spark_in_start() -> None:
    with ThreadPoolExecutor(max_workers=3) as executor:
        executor.submit(
            run_spark_streaming("BTC", BTC_TOPIC_NAME, BTC_AVERAGE_TOPIC_NAME)
        )
        executor.submit(
            run_spark_streaming("ETH", ETH_TOPIC_NAME, ETH_AVERAGE_TOPIC_NAME)
        )


if __name__ == "__main__":
    spark_in_start()
