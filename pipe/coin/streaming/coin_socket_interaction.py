"""
COIN Streaming socket initialiation
"""

import asyncio
from typing import Any
from concurrent.futures import TimeoutError, CancelledError, ThreadPoolExecutor
from coin.core.market.data_format import CoinMarket, CoinNameAndSymbol
from coin.core.market.coin_abstract_class import CoinPresentPriceMarketPlace
from coin.core.market.util_func import worker
from coin.core.settings.properties import market_setting
from coin.core.settings.create_log import log


class CoinPresentPriceWebsocket(CoinPresentPriceMarketPlace):
    """
    Coin Stream
    """

    def __init__(self) -> None:
        self.market_env = market_setting("socket")

    async def coin_present_architecture(self) -> None:
        queue = asyncio.Queue()
        workers = [asyncio.create_task(worker(queue)) for _ in range(3)]  # 워커 시작

        coroutines: list[Any] = [
            self.market_env[i]["api"].get_present_websocket(queue)
            for i in self.market_env
        ]
        await asyncio.gather(*coroutines)

        await queue.join()
        for w in workers:
            w.cancel()
