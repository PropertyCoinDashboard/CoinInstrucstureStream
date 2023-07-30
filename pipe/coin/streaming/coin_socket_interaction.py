"""
COIN Streaming socket initialiation
"""
import asyncio
from pathlib import Path
from typing import Any, Coroutine, NoReturn
from asyncio.exceptions import TimeoutError, CancelledError

from coin.core.market.coin_abstract_class import CoinPresentPriceMarketPlace
from coin.core.settings.properties import market_setting
from coin.core.settings.create_log import log
from coin.core.market.data_format import CoinMarket
from coin.core.data_mq.data_interaction import produce_sending


present_path = Path(__file__).parent
logger = log(f"{present_path}/log/worker.log", "worker")


class CoinPresentPriceWebsocket(CoinPresentPriceMarketPlace):
    """
    Coin Stream
    """

    def __init__(self, market_type: str = "socket") -> None:
        self.market_env = market_setting(market_type)
        self.logger = log(f"{present_path}/log/worker.log", "worker")

    async def coin_present_architecture(self, symbol: str) -> Coroutine[Any, Any, None]:
        try:
            coroutines: list[Any] = [
                self.market_env[i]["api"].get_present_websocket(symbol)
                for i in self.market_env
            ]
            await asyncio.gather(*coroutines, return_exceptions=True)
        except (TimeoutError, CancelledError) as e:
            self.logger.error("진행하지 못했습니다 --> %s", e)
