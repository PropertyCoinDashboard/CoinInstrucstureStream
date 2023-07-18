import tracemalloc

tracemalloc.start()

from coin_apis import (
    UpBitCoinFullRequest,
    BithumbCoinFullRequest,
    KorbitCoinFullRequest,
)
from data_format import CoinMarketData, CoinMarket
from typing import Any

import asyncio
from concurrent.futures import ThreadPoolExecutor

"""
임시로 작성함 
리팩토링 필수 (pydantic morden architecture 로 변경 완료) (O)
1. 동시성 + 비동기  -> 진행하기 (O)
2. 중복되는 메서드 줄이기  (O)
3. 과도한 책임 줄이기
"""


async def coin_present_architecture(
    market: str,
    time: str,
    coin_symbol: str,
    api: Any,
    parameter: tuple[str, str, str, str, str, str],
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
        with ThreadPoolExecutor(max_workers=3) as executer:
            tasks = [
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
