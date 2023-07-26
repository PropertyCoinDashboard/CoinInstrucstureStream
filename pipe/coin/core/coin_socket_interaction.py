"""
COIN Streaming socket initialiation
"""

import asyncio
from concurrent.futures import TimeoutError, CancelledError
from concurrent.futures import ThreadPoolExecutor
from coin.core.market.data_format import CoinMarket, CoinNameAndSymbol
from coin.core.market.coin_abstract_class import CoinPresentPriceMarketPlace


class CoinPresentPriceWebsocket(CoinPresentPriceMarketPlace):
    """
    Coin Stream
    """

    def __init__(self) -> None:
        super().__init__(conn_type="socket")

    async def ss():
        pass
