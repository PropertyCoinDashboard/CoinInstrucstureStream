from pydantic import BaseModel
from typing import Mapping, Any


class CoinSymbol(BaseModel):
    """
    Subject:
        - simpleist coin symbol\n
    Returns:
        - "BTC"
    """

    coin_symbol: str


class CoinMarketData(BaseModel):
    """Coin price data schema
    Args:
        - BaseModel (_type_): pydantic BaseModel 으로 구현 했습니다  \n
    Returns:
        -  {
            "market": "upbit-BTC",
            "time": 1689659170616,
            "coin_symbol": "BTC",
            "data": {
                "opening_price": 38761000.0,
                "high_price": 38828000.0,
                "low_price": 38470000.0,
                "prev_closing_price": 38742000.0,
                "acc_trade_volume_24h": 2754.0481778
            }
        }
    """

    market: str
    coin_symbol: str
    parameter: dict[str, Any]

    @classmethod
    def from_api(
        cls,
        market: str,
        coin_symbol: str,
        api: Mapping[str, Any],
        parameter: tuple[str],
    ) -> "CoinMarketData":
        price_data: dict[str, float] = {
            parameter[0]: int(api[parameter[0]]),
            parameter[1]: float(api[parameter[1]]),
            parameter[2]: float(api[parameter[2]]),
            parameter[3]: float(api[parameter[3]]),
            parameter[4]: float(api[parameter[4]]),
            parameter[5]: float(api[parameter[5]]),
        }

        return cls(market=market, coin_symbol=coin_symbol, parameter=price_data)
