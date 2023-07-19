"""

Coin async present price kafka data streaming 
"""
import asyncio
import tracemalloc
from asyncio.exceptions import CancelledError
from typing import Any, Coroutine

from mq.data_interaction import produce_sending
from setting.create_log import log
from pydantic.errors import PydanticUserError

from core.data_format import CoinMarketData, CoinMarket
from core.coin_apis import (
    UpBitCoinFullRequest,
    BithumbCoinFullRequest,
    KorbitCoinFullRequest,
)


tracemalloc.start()
logger = log()
# market 정보
MARKET: dict[str, dict[str, Any]] = {
    "upbit": {
        "api": UpBitCoinFullRequest,
        "timestamp": "trade_timestamp",
        "parameter": (
            "opening_price",
            "high_price",
            "low_price",
            "prev_closing_price",
            "acc_trade_volume_24h",
        ),
    },
    "bithum": {
        "api": BithumbCoinFullRequest,
        "timestamp": "date",
        "parameter": (
            "opening_price",
            "max_price",
            "min_price",
            "prev_closing_price",
            "units_traded_24H",
        ),
    },
    "korbit": {
        "api": KorbitCoinFullRequest,
        "timestamp": "timestamp",
        "parameter": ("open", "high", "low", "last", "volume"),
    },
}


async def coin_present_architecture(
    market: str,
    time: str,
    coin_symbol: str,
    api: Any,
    parameter: tuple[str, str, str, str, str],
) -> str:
    """
    Coin present price architecture

    Args:
        market (str): marketname-coinsymbol
        coin_symbol (str): coinsymbol("BTC".."EHT"...)
        api (Any): coin_apis.py in class
        parameter (tuple[str * 6]): search parameter

    Returns:
        CoinMarketData: pydantic in JSON transformation
    """
    try:
        api_response = api(coin_name=coin_symbol.upper()).get_coin_present_price()
        market_time = api_response[time]

        return CoinMarketData.from_api(
            market=market,
            coin_symbol=coin_symbol,
            time=market_time,
            api=api_response,
            parameter=parameter,
        ).model_dump()
    except PydanticUserError as error:
        logger.error("Exception occurred: %s", error)


class CoinPresentPriceMarketPlace:
    """
    Coin present price market place
    """

    @classmethod
    async def get_market_present_price(cls, market: str, coin_symbol: str) -> str:
        """
        Get market present price

        Args:
            market (str): market name
            coin_symbol (str): coin symbol

        Returns:
            str: market data as a string
        """
        market_info = MARKET[market]
        return await coin_present_architecture(
            market=f"{market}-{coin_symbol.upper()}",
            coin_symbol=coin_symbol,
            time=market_info["timestamp"],
            api=market_info["api"],
            parameter=market_info["parameter"],
        )

    @classmethod
    async def total_full_request(cls, coin_symbol: str, topic_name: str) -> None:
        """
        Total full request

        Args:
            coin_symbol (str): coin symbol
            topic_name (str): topic name
        """
        while True:
            await asyncio.sleep(1)
            try:
                tasks: list[Coroutine[Any, Any, dict[str, Any]]] = [
                    cls.get_market_present_price(market=market, coin_symbol=coin_symbol)
                    for market in MARKET
                ]
                market_result = await asyncio.gather(*tasks, return_exceptions=True)

                schema = CoinMarket(
                    **{
                        market: result
                        for market, result in zip(MARKET.keys(), market_result)
                        if result is not None
                    }
                ).model_dump_json(indent=4)
                produce_sending(topic_name, message=schema)
            except (TimeoutError, CancelledError) as error:
                logger.error("Data transmission failed: %s", error)
