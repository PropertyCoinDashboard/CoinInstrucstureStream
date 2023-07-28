"""
COIN Streaming socket initialiation
"""
import json
import asyncio
from pathlib import Path
from typing import Any, Coroutine, NoReturn
from asyncio.exceptions import TimeoutError, CancelledError

from coin.core.market.coin_abstract_class import CoinPresentPriceMarketPlace
from coin.core.settings.properties import market_setting
from coin.core.settings.create_log import log


present_path = Path(__file__).parent
logger = log(f"{present_path}/log/worker.log", "worker")


class CoinPresentPriceWebsocket(CoinPresentPriceMarketPlace):
    """
    Coin Stream
    """

    def __init__(self, market_type: str = "socket") -> None:
        self.market_env = market_setting(market_type)
        self.logger = log(f"{present_path}/log/worker.log", "worker")

    async def worker(self, input_queue: asyncio.Queue) -> Coroutine[Any, Any, NoReturn]:
        while True:
            url, message = await input_queue.get()
            self.logger.info(f"Message from {url}: {message}")
            input_queue.task_done()

    async def coin_present_architecture(self) -> Coroutine[Any, Any, None]:
        try:
            queue = asyncio.Queue()
            workers = [asyncio.create_task(self.worker(queue)) for _ in range(3)]

            coroutines: list[Any] = [
                self.market_env[i]["api"].get_present_websocket(queue, "BTC")
                for i in self.market_env
            ]
            await asyncio.gather(*coroutines)

            await queue.join()
            for w in workers:
                w.cancel()
        except (TimeoutError, CancelledError) as e:
            self.logger.error("진행하지 못했습니다 --> %s", e)
