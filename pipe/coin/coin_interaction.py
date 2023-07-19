import tracemalloc

tracemalloc.start()

from typing import Any, Coroutine
from setting.create_log import log

from kafka_interaction import produce_sending
from schema.data_format import CoinMarketData, CoinMarket
from schema.coin_apis import (
    UpBitCoinFullRequest,
    BithumbCoinFullRequest,
    KorbitCoinFullRequest,
)

import asyncio
from asyncio.exceptions import TimeoutError
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures._base import Error as ThreadPoolError


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
    Subject:
        - coin_present_price 정형화 \n
    Args:
        - market (str): marketname-coinsymbol
        - coin_symbol (str): coinsymbol("BTC".."EHT"...)
        - api (Any): coin_apis.py in class
        - parameter (tuple[str * 6]): search parameter \n
    Returns:
        - CoinMarketData: pydantic in JSON transformation
    """

    api_response = api(coin_name=coin_symbol.upper()).get_coin_present_price()
    market_time = api_response[time]

    return CoinMarketData.from_api(
        market=market,
        coin_symbol=coin_symbol,
        time=market_time,
        api=api_response,
        parameter=parameter,
    ).model_dump()


class CoinPresentPriceMarketPlace:
    """
    Subject:
        - coin_preset_price_total_schema \n
    Returns:
        - CoinMarket: pydantic in JSON transformation\n
    """

    @classmethod
    async def get_market_present_price(cls, market: str, coin_symbol: str) -> str:
        market_info = MARKET[market]
        return await coin_present_architecture(
            market=f"{market}-{coin_symbol.upper()}",
            coin_symbol=coin_symbol,
            time=market_info["timestamp"],
            api=market_info["api"],
            parameter=market_info["parameter"],
        )

    @classmethod
    async def total_full_request(cls, coin_symbol: str) -> None:
        try:
            with ThreadPoolExecutor(max_workers=3) as executer:
                tasks: list[Coroutine[Any, Any, dict[str, Any]]] = [
                    cls.get_market_present_price(market=market, coin_symbol=coin_symbol)
                    for market in MARKET
                ]

                market_result = await asyncio.gather(*tasks, return_exceptions=True)
                schema = CoinMarket(
                    **{
                        market: result
                        for market, result in zip(MARKET.keys(), market_result)
                    }
                ).model_dump_json(indent=4)
                logger.info(f"데이터 전송 --> \n{schema}\n")
                produce_sending(topic="test", message=schema)
        except (ThreadPoolError, TimeoutError) as e:
            logger.error(f"에러가 일어났습니다 --> \n{e}\n")
