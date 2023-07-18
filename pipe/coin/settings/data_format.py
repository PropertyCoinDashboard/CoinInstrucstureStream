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


class CoinMarket(BaseModel):
    """
    Subject:
        - coin_preset_price_total_schema \n
    Returns:
        - pydantic in JSON transformation\n
        >>> {
            "upbit": {
                "name": "upbit-ETH",
                "timestamp": 1689633864.89345,
                "data": {
                    "opening_price": 2455000.0,
                    "closing_price": 2439000.0,
                    "max_price": 2462000.0,
                    "min_price": 2431000.0,
                    "prev_closing_price": 2455000.0,
                    "acc_trade_volume_24h": 11447.92825886,
                }
            }
        }
    """

    upbit: str
    bithum: str
    korbit: str


class CoinMarketData(BaseModel):
    """Coin price data schema
    Args:
        - BaseModel (_type_): pydantic BaseModel 으로 구현 했습니다  \n
    Returns:
        >>>  {
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
    time: int
    coin_symbol: str
    parameter: dict[str, Any]

    @classmethod
    def from_api(
        cls,
        market: str,
        time: int,
        coin_symbol: str,
        api: Mapping[str, Any],
        parameter: tuple[str, str, str, str, str],
    ) -> "CoinMarketData":
        price_data: dict[str, Any] = {key: api[key] for key in parameter}

        return cls(
            market=market, time=time, coin_symbol=coin_symbol, parameter=price_data
        )
