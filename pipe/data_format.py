from pydantic import BaseModel
from typing import Mapping, Any


class CoinSymbol(BaseModel):
    coin_symbol: str


class CoinMarketData(BaseModel):
    market: str
    time: int
    coin_symbol: str
    data: dict[str, Any]

    @classmethod
    def from_api(
        cls,
        market: str,
        time: int,
        coin_symbol: str,
        api: Mapping[str, Any],
        data: tuple[str],
    ) -> "CoinMarketData":
        price_data: dict[str, float] = {
            data[0]: float(api[data[0]]),
            data[1]: float(api[data[1]]),
            data[2]: float(api[data[2]]),
            data[3]: float(api[data[3]]),
            data[4]: float(api[data[4]]),
        }

        return cls(market=market, time=time, coin_symbol=coin_symbol, data=price_data)
