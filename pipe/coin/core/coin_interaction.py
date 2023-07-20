"""
Coin async present price kafka data streaming 
"""
import asyncio
import tracemalloc
from asyncio.exceptions import CancelledError
from typing import Any, Coroutine

from pydantic.errors import PydanticUserError


from coin.core.data_format import CoinMarket, CoinMarketData
from coin.core.coin_apis import (
    UpBitCoinFullRequest,
    BithumbCoinFullRequest,
    KorbitCoinFullRequest,
)

from coin.core.config.create_log import log
from coin.core.config.properties import market_setting
from coin.core.data_mq.data_interaction import produce_sending


# 기본 정보
tracemalloc.start()
logger = log()

# market 정보
market_env: dict[str, dict[str, Any]] = market_setting(
    upbit=UpBitCoinFullRequest,
    bithumb=BithumbCoinFullRequest,
    korbit=KorbitCoinFullRequest,
)


async def coin_present_architecture(
    market: str,
    time: str,
    coin_symbol: str,
    api: Any,
    data: tuple[str, str, str, str, str],
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
            time=market_time,
            api=api_response,
            data=data,
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
        market_info = market_env[market]
        return await coin_present_architecture(
            market=f"{market}-{coin_symbol.upper()}",
            coin_symbol=coin_symbol,
            time=market_info["timestamp"],
            api=market_info["api"],
            data=market_info["parameter"],
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
                    for market in market_env
                ]
                market_result = await asyncio.gather(*tasks, return_exceptions=True)
                schema: str = CoinMarket(
                    **{
                        market: result
                        for market, result in zip(market_env.keys(), market_result)
                        if result is not None
                    }
                ).model_dump()
                produce_sending(topic_name, message=schema)
            except (TimeoutError, CancelledError) as error:
                logger.error("Data transmission failed: %s", error)
