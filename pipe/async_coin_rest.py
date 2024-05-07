"""
실시간 테스트 
"""

import asyncio
from coin.core.coin_rest_interaction import CoinPresentPriceReponseAPI


async def btc_present_start() -> None:
    """
    bitcoin kafak stream
    """
    await CoinPresentPriceReponseAPI().total_pull_request("BTC")


async def eth_present_start() -> None:
    """
    ethereum kafak stream
    """
    await CoinPresentPriceReponseAPI().total_pull_request("ETH")


async def be_present_gether() -> None:
    """
    kafka async stream
    """
    tasks = [
        asyncio.create_task(btc_present_start()),
        asyncio.create_task(eth_present_start()),
    ]
    await asyncio.gather(*tasks, return_exceptions=True)


async def data_sending_start() -> None:
    await be_present_gether()


if __name__ == "__main__":
    asyncio.run(btc_present_start())
