import tracemalloc

tracemalloc.start()

from coin_apis import (
    UpBitCoinFullRequest,
    BithumbCoinFullRequest,
    KorbitCoinFullRequest,
)
from settings.data_format import CoinMarketData, CoinMarket
from settings.create_log import log
from typing import Any, Coroutine

import asyncio
from asyncio.exceptions import TimeoutError
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures._base import Error as ThreadPoolError


logging = log()


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
    ).model_dump_json(indent=4)


class CoinPresentPriceMarketPlace:
    """
    Subject:
        - coin_preset_price_total_schema \n
    Returns:
        - CoinMarket: pydantic in JSON transformation\n
    """

    @classmethod
    async def upbit_present(cls, coin_symbol: str) -> str:
        parameter = (
            "opening_price",
            "high_price",
            "low_price",
            "prev_closing_price",
            "acc_trade_volume_24h",
        )

        return await coin_present_architecture(
            market=f"upbit-{coin_symbol.upper()}",
            coin_symbol=coin_symbol,
            time="trade_timestamp",
            api=UpBitCoinFullRequest,
            parameter=parameter,
        )

    @classmethod
    async def bithum_present(cls, coin_symbol: str) -> str:
        parameter = (
            "opening_price",
            "max_price",
            "min_price",
            "prev_closing_price",
            "units_traded_24H",
        )

        return await coin_present_architecture(
            market=f"bithum-{coin_symbol.upper()}",
            coin_symbol=coin_symbol,
            time="date",
            api=BithumbCoinFullRequest,
            parameter=parameter,
        )

    @classmethod
    async def korbit_present(cls, coin_symbol: str) -> str:
        parameter = ("open", "high", "low", "last", "volume")

        return await coin_present_architecture(
            market=f"korbit-{coin_symbol.upper()}",
            coin_symbol=coin_symbol,
            time="timestamp",
            api=KorbitCoinFullRequest,
            parameter=parameter,
        )

    @classmethod
    async def total_full_request(cls, coin_symbol: str) -> str:
        try:
            with ThreadPoolExecutor(max_workers=3) as executer:
                tasks: list[Coroutine[Any, Any, dict[str, Any]]] = [
                    cls.upbit_present(coin_symbol=coin_symbol),
                    cls.bithum_present(coin_symbol=coin_symbol),
                    cls.korbit_present(coin_symbol=coin_symbol),
                ]

                upbit, bithumb, korbit = await asyncio.gather(
                    *tasks, return_exceptions=True
                )
                schema = CoinMarket(
                    upbit=upbit, bithum=bithumb, korbit=korbit
                ).model_dump_json()

                return schema
        except (ThreadPoolError, TimeoutError) as e:
            logging.error(f"에러가 일어났습니다 --> \n{e}\n")


def start():
    return CoinPresentPriceMarketPlace().total_full_request("BTC")


asyncio.run(start())
