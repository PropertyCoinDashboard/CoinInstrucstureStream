from coin.core.data_mq.data_admin import new_topic_initialization, delete_all_topics
from coin.core.setting.properties import (
    BTC_TOPIC_NAME,
    ETH_TOPIC_NAME,
    REST_BTC_AVERAGE_TOPIC_NAME,
    REST_ETH_AVERAGE_TOPIC_NAME,
    UPBIT_BTC_REAL_TOPIC_NAME,
    BITHUMB_BTC_REAL_TOPIC_NAME,
    KORBIT_BTC_REAL_TOPIC_NAME,
    COINONE_BTC_REAL_TOPIC_NAME,
    SOCKET_BTC_AVERAGE_TOPIC_NAME,
    SOCKET_ETH_AVERAGE_TOPIC_NAME,
)


def data_sending_start() -> None:
    """
    Topic create
    """
    topic = [
        UPBIT_BTC_REAL_TOPIC_NAME,
        BITHUMB_BTC_REAL_TOPIC_NAME,
        KORBIT_BTC_REAL_TOPIC_NAME,
        COINONE_BTC_REAL_TOPIC_NAME,
        BTC_TOPIC_NAME,
        ETH_TOPIC_NAME,
        REST_ETH_AVERAGE_TOPIC_NAME,
        REST_BTC_AVERAGE_TOPIC_NAME,
        SOCKET_BTC_AVERAGE_TOPIC_NAME,
        SOCKET_ETH_AVERAGE_TOPIC_NAME,
    ]
    partition = [4] * len(topic)
    replication = [3] * len(topic)

    return new_topic_initialization(
        topic=topic, partition=partition, replication_factor=replication
    )


if __name__ == "__main__":
    data_sending_start()
