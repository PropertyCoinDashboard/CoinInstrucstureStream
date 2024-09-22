# import asyncio
# from korea_exchange.websocket_client import CoinPresentPriceWebsocket


# async def coin_present_websocket_btc() -> None:
#     await CoinPresentPriceWebsocket("BTC").coin_present_architecture()


# async def coin_present_websocket() -> None:
#     task = [
#         asyncio.create_task(coin_present_websocket_btc()),
#         # asyncio.create_task(coin_present_websocket_eth()),
#     ]
#     await asyncio.gather(*task, return_exceptions=False)


# if __name__ == "__main__":
#     asyncio.run(coin_present_websocket())
"""
실시간 테스트 
"""

import asyncio
from korea_exchange.rest_client import CoinPresentPriceReponseAPI

# from .core.coin_rest_interaction import CoinPresentPriceReponseAPI


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
    await asyncio.gather(*tasks, return_exceptions=False)


async def data_sending_start() -> None:
    await be_present_gether()


if __name__ == "__main__":
    asyncio.run(data_sending_start())
