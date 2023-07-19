"""
실시간 테스트 
"""

import asyncio

from core.coin_interaction import CoinPresentPriceMarketPlace
from mq.data_admin import new_topic_initalization
from setting.properties import BIT_TOPIC_NAME, ETHER_TOPIC_NAME


async def btc_present_start() -> None:
    """
    kafak test
    """
    await CoinPresentPriceMarketPlace.total_full_request("BTC", BIT_TOPIC_NAME)


async def eth_present_start() -> None:
    """
    kafak test
    """
    await CoinPresentPriceMarketPlace.total_full_request("ETC", ETHER_TOPIC_NAME)


async def be_present_gether() -> None:
    """
    kafak test
    """
    tasks = [
        asyncio.create_task(btc_present_start()),
        asyncio.create_task(eth_present_start()),
    ]
    await asyncio.gather(*tasks, return_exceptions=True)


async def start() -> None:
    """
    Topic create test
    """
    topic = [BIT_TOPIC_NAME, ETHER_TOPIC_NAME]
    partition = [2, 2]
    replication = [2, 2]

    new_topic_initalization(
        topic=topic, partition=partition, replication_factor=replication
    )

    asyncio.sleep(1)
    await be_present_gether()


asyncio.run(start())
