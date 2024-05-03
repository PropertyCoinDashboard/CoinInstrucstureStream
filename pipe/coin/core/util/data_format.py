"""
Coin present data format architecture
"""

from __future__ import annotations
from typing import Any
from decimal import Decimal, ROUND_HALF_UP
from pydantic import BaseModel, validator


class CoinMarket(BaseModel):
    """
    Subject:
        - coin_preset_price_total_schema \n
    Returns:
        - pydantic in JSON transformation \n
        >>> {
                "upbit": {
                    "name": "upbit-ETH",
                    "timestamp": 1689633864.89345,
                    "data": {
                        "opening_price": 2455000.0,
                        "trade_price": 38100000.0
                        "max_price": 2462000.0,
                        "min_price": 2431000.0,
                        "prev_closing_price": 2455000.0,
                        "acc_trade_volume_24h": 11447.92825886,
                    }
                },
                ....
            }
    """

    upbit: dict[str, Any]
    bithumb: dict[str, Any]
    coinone: dict[str, Any]
    korbit: dict[str, Any]
    gopax: dict[str, Any]


class PriceData(BaseModel):
    """코인 현재 가격가

    Args:
        BaseModel (_type_): pydantic

    Returns:
        _type_: Decimal type
    """

    opening_price: Decimal
    trade_price: Decimal
    max_price: Decimal
    min_price: Decimal
    prev_closing_price: Decimal
    acc_trade_volume_24h: Decimal

    @validator("*", pre=True)
    @classmethod
    def round_three_place_adjust(cls, value: Any) -> Decimal:
        """반올림

        Args:
            value (_type_): 들어올 값 PriceData parameter

        Returns:
            Decimal: _description_
        """
        return Decimal(value=value).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)


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
                    "trade_price": 38100000.0
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
    data: PriceData

    @classmethod
    def _create_price_data(cls, api: dict[str, str], data: list[str]) -> PriceData:
        try:
            return PriceData(
                opening_price=Decimal(api[data[0]]),
                trade_price=Decimal(api[data[1]]),
                max_price=Decimal(api[data[2]]),
                min_price=Decimal(api[data[3]]),
                prev_closing_price=Decimal(api[data[4]]),
                acc_trade_volume_24h=Decimal(api[data[5]]),
            )
        except KeyError as e:
            raise KeyError(f"Key {e} not found in API response") from e

    @classmethod
    def from_api(
        cls,
        market: str,
        time: int,
        coin_symbol: str,
        api: dict[str, Any],
        data: list[str],
    ) -> CoinMarketData:
        """다음과 같은 dictionary를 만들기 위한 pydantic json model architecture
        >>>  {
            "market": "upbit-BTC",
            "time": 1689659170616,
            "coin_symbol": "BTC",
            "data": {
                "opening_price": 38761000.0,
                "trade_price": 38100000.0
                "high_price": 38828000.0,
                "low_price": 38470000.0,
                "prev_closing_price": 38742000.0,
                "acc_trade_volume_24h": 2754.0481778
            }
        }
        Args:
            market (str): 거래소 이름
            time (int): 거래 시간
            coin_symbol (str): 심볼
            api (Mapping[str, Any]): 거래소 API
            data (list[str, str, str, str, str, str]): 사용할 파라미터 \n
        Returns:
            CoinMarketData: _description_
        """
        price_data: PriceData = cls._create_price_data(api=api, data=data)
        return cls(
            market=market,
            time=time,
            coin_symbol=coin_symbol,
            data=price_data,
        )
