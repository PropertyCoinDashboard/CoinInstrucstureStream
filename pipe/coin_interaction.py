from coin_apis import (
    UpBitCoinFullRequest,
    BithumbCoinFullRequest,
    KorbitCoinFullRequest,
)
from data_format import CoinMarketData, CoinPrice, asdict
from typing import *


"""
임시로 작성함 
리팩토링 필수 
1. 동시성 + 비동기 
2. 중복되는 메서드 줄이기 
3. 과도한 책임 줄이기
"""


def upbit_coin_present(coin_name: str) -> dict[str, Any]:
    upbit_present = UpBitCoinFullRequest(coin_name=coin_name).get_coin_present_price()
    return asdict(
        CoinMarketData(
            market=f"upbit-{coin_name.upper()}",
            time=upbit_present["trade_timestamp"],
            coin_symbol=coin_name,
            data=CoinPrice(
                opening_price=upbit_present["opening_price"],
                high_price=upbit_present["high_price"],
                low_price=upbit_present["low_price"],
                prev_closing_price=upbit_present["prev_closing_price"],
                volumne_24=upbit_present["acc_trade_volume_24h"],
            ),
        )
    )


def bithum_coin_present(coin_name: str) -> dict[str, Any]:
    bit_present = BithumbCoinFullRequest(coin_name=coin_name).get_coin_present_price()
    return asdict(
        CoinMarketData(
            market=f"bithum-KRW-{coin_name.upper()}",
            time=bit_present["date"],
            coin_symbol=coin_name,
            data=CoinPrice(
                opening_price=bit_present["opening_price"],
                high_price=bit_present["max_price"],
                low_price=bit_present["min_price"],
                prev_closing_price=bit_present["prev_closing_price"],
                volumne_24=bit_present["units_traded_24H"],
            ),
        )
    )


def korbit_coin_present(coin_name: str) -> dict[str, Any]:
    korbit_present = KorbitCoinFullRequest(coin_name=coin_name).get_coin_present_price()
    return asdict(
        CoinMarketData(
            market=f"korbit-KRW-{coin_name.upper()}",
            time=korbit_present["timestamp"],
            coin_symbol=coin_name,
            data=CoinPrice(
                opening_price=korbit_present["open"],
                high_price=korbit_present["high"],
                low_price=korbit_present["low"],
                prev_closing_price=korbit_present["last"],
                volumne_24=korbit_present["volume"],
            ),
        )
    )


if __name__ == "__main__":
    coin_name = "BTC"
    a = upbit_coin_present(coin_name)
    b = bithum_coin_present(coin_name)
    c = korbit_coin_present(coin_name)

    print(a)
    print(b)
    print(c)
