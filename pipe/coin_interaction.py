from coin_apis import (
    UpBitCoinFullRequest,
    BithumbCoinFullRequest,
    KorbitCoinFullRequest,
    CoinFullRequest,
)
from data_format import CoinMarketData
from typing import *


"""
임시로 작성함 
리팩토링 필수 (pydantic morden architecture 로 변경 완료) (O)
1. 동시성 + 비동기  -> 진행하기
2. 중복되는 메서드 줄이기  (O)
3. 과도한 책임 줄이기
"""


def coin_present_architecture(
    market: str,
    coin_symbol: str,
    api: Any,
    parameter: tuple[str, str, str, str, str, str],
) -> str:
    """coin_present_price 정형화

    Args:
        market (str): marketname-coinsymbol
        coin_symbol (str): coinsymbol("BTC".."EHT"...)
        api (dict[str, Any]  |  CoinFullRequest): coin_apis.py in class
        parameter (tuple[str]): search parameter

    Returns:
        CoinMarketData: pydantic in JSON transformation
    """

    api = api(coin_name=coin_symbol.upper()).get_coin_present_price()

    return CoinMarketData.from_api(
        market=market, coin_symbol=coin_symbol, api=api, parameter=parameter
    ).model_dump_json(indent=4)


def upbit_present(coin_name: str) -> str:
    parameter = (
        "trade_timestamp",
        "opening_price",
        "high_price",
        "low_price",
        "prev_closing_price",
        "acc_trade_volume_24h",
    )

    return coin_present_architecture(
        market=f"upbit-{coin_name.upper()}",
        coin_symbol=coin_name,
        api=UpBitCoinFullRequest,
        parameter=parameter,
    )


def bithum_present(coin_name: str) -> str:
    parameter = (
        "date",
        "opening_price",
        "max_price",
        "min_price",
        "prev_closing_price",
        "units_traded_24H",
    )

    return coin_present_architecture(
        market=f"bithum-{coin_name.upper()}",
        coin_symbol=coin_name,
        api=BithumbCoinFullRequest,
        parameter=parameter,
    )


def korbit_present(coin_name: str) -> str:
    parameter = ("timestamp", "open", "high", "low", "last", "volume")

    return coin_present_architecture(
        market=f"korbit-{coin_name.upper()}",
        coin_symbol=coin_name,
        api=KorbitCoinFullRequest,
        parameter=parameter,
    )
