"""
실시간 테스트 
"""

import asyncio

from coin.core.coin_interaction import CoinPresentPriceMarketPlace
from coin.core.data_mq.data_admin import new_topic_initialization
from coin.core.config.properties import (
    BTC_TOPIC_NAME,
    ETH_TOPIC_NAME,
    BTC_AVERAGE_TOPIC_NAME,
    ETH_AVERAGE_TOPIC_NAME,
)


async def btc_present_start() -> None:
    """
    bitcoin kafak stream
    """
    await CoinPresentPriceMarketPlace.total_full_request("BTC", BTC_TOPIC_NAME)


async def eth_present_start() -> None:
    """
    ethereum kafak stream
    """
    await CoinPresentPriceMarketPlace.total_full_request("ETH", ETH_TOPIC_NAME)


async def be_present_gether() -> None:
    """
    kafka async steam
    """
    tasks = [
        asyncio.create_task(btc_present_start()),
        asyncio.create_task(eth_present_start()),
    ]
    await asyncio.gather(*tasks, return_exceptions=True)


async def data_sending_start() -> None:
    """
    Topic create
    """
    topic = [
        BTC_TOPIC_NAME,
        ETH_TOPIC_NAME,
        ETH_AVERAGE_TOPIC_NAME,
        BTC_AVERAGE_TOPIC_NAME,
    ]
    partition = [2, 2, 2, 2]
    replication = [2, 2, 2, 2]

    new_topic_initialization(
        topic=topic, partition=partition, replication_factor=replication
    )
    asyncio.sleep(1)
    await be_present_gether()


if __name__ == "__main__":
    asyncio.run(data_sending_start())
