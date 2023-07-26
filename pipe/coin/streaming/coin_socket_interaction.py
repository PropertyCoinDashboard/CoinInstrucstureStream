"""
COIN Streaming socket initialiation
"""

import asyncio
from typing import Any
from pathlib import Path
from asyncio.exceptions import TimeoutError, CancelledError

from coin.core.market.data_format import CoinMarket, CoinNameAndSymbol
from coin.core.market.coin_abstract_class import CoinPresentPriceMarketPlace
from coin.core.settings.properties import market_setting
from coin.core.settings.create_log import log


present_path = Path(__file__).parent
logger = log(f"{present_path}/log/worker.log", "worker")


class CoinPresentPriceWebsocket(CoinPresentPriceMarketPlace):
    """
    Coin Stream
    """

    def __init__(self) -> None:
        self.market_env = market_setting("socket")

    async def worker(self, input_queue: asyncio.Queue) -> None:
        """빼는곳

        Args:
            queue (asyncio.Queue): 큐
        """
        while True:
            url, message = await input_queue.get()
            logger.info(f"Message from {url}: {message}")
            input_queue.task_done()

    async def coin_present_architecture(self) -> None:
        try:
            queue = asyncio.Queue()
            workers = [
                asyncio.create_task(self.worker(queue)) for _ in range(3)
            ]  # 워커 시작

            coroutines: list[Any] = [
                self.market_env[i]["api"].get_present_websocket(queue)
                for i in self.market_env
            ]
            await asyncio.gather(*coroutines)

            await queue.join()
            for w in workers:
                w.cancel()
        except (TimeoutError, CancelledError) as e:
            logger.error("진행하지 못했습니다 --> %s", e)
