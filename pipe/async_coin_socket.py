"""
COIN Streaming socket initialiation
"""
import asyncio
import tracemalloc
from typing import Any, Coroutine
from asyncio.exceptions import TimeoutError, CancelledError


from coin.core.setting.factory_api import load_json
from coin.core.util.create_log import SocketLogCustomer


class CoinPresentPriceWebsocket:
    """
    Coin Stream
    """

    def __init__(self, market_type: str = "socket") -> None:
        tracemalloc.start()
        self.market_env = load_json(market_type)
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


if __name__ == "__main__":
    asyncio.run(CoinPresentPriceWebsocket().coin_present_architecture("BTC"))
