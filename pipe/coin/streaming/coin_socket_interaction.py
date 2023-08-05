"""
COIN Streaming socket initialiation
"""
import asyncio
import tracemalloc
from pathlib import Path
from typing import Any, Coroutine
from asyncio.exceptions import TimeoutError, CancelledError


from coin.core.settings.properties import market_setting
from coin.core.settings.create_log import SocketLogCustomer


present_path = Path(__file__).parent


class CoinPresentPriceWebsocket:
    """
    Coin Stream
    """

    def __init__(self, market_type: str = "socket") -> None:
        tracemalloc.start()
        self.market_env = market_setting(market_type)
        self.logger = SocketLogCustomer()

    async def coin_present_architecture(self, symbol: str) -> Coroutine[Any, Any, None]:
        try:
            coroutines: list[Any] = [
                self.market_env[i]["api"].get_present_websocket(symbol)
                for i in self.market_env
            ]
            await asyncio.gather(*coroutines, return_exceptions=True)
        except (TimeoutError, CancelledError) as error:
            self.logger.error_log(
                error_type="worker", message=f"진행하지 못했습니다 --> {error}"
            )
