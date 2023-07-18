from coin_apis import (
    UpBitCoinFullRequest,
    BithumbCoinFullRequest,
    KorbitCoinFullRequest,
)
from data_format import CoinMarketData
from typing import *


"""
임시로 작성함 
리팩토링 필수 
1. 동시성 + 비동기 
2. 중복되는 메서드 줄이기 
3. 과도한 책임 줄이기
"""


def coin_present_architecture(
    market: str, time: int, coin_symbol: str, api: Any, data: tuple[str]
) -> "CoinMarketData":
    return CoinMarketData.from_api(
        market=market, time=time, coin_symbol=coin_symbol, api=api, data=data
    )


def upbit_present(coin_name: str) -> dict[str, Any]:
    upbit_present: dict[str, Any] = UpBitCoinFullRequest(
        coin_name=coin_name
    ).get_coin_present_price()

    return coin_present_architecture(
        market=f"upbit-{coin_name.upper()}",
        time=upbit_present["trade_timestamp"],
        coin_symbol=coin_name,
        api=upbit_present,
        data=(
            "opening_price",
            "high_price",
            "low_price",
            "prev_closing_price",
            "acc_trade_volume_24h",
        ),
    )


def bithum_present(coin_name: str) -> dict[str, Any]:
    bit_present: dict[str, Any] = BithumbCoinFullRequest(
        coin_name=coin_name
    ).get_coin_present_price()

    return coin_present_architecture(
        market=f"bithum-{coin_name.upper()}",
        time=bit_present["date"],
        coin_symbol=coin_name,
        api=bit_present,
        data=(
            "opening_price",
            "max_price",
            "min_price",
            "prev_closing_price",
            "units_traded_24H",
        ),
    )


def korbit_present(coin_name: str) -> dict[str, Any]:
    korbit_present: dict[str, Any] = KorbitCoinFullRequest(
        coin_name=coin_name
    ).get_coin_present_price()

    return coin_present_architecture(
        market=f"korbit-{coin_name.upper()}",
        time=korbit_present["timestamp"],
        coin_symbol=coin_name,
        api=korbit_present,
        data=("open", "high", "low", "last", "volume"),
    )


if __name__ == "__main__":
    coin_name = "BTC"
    a = upbit_present(coin_name)
    b = bithum_present(coin_name)
    c = korbit_present(coin_name)

    print(a)
    print(b)
    print(c)
