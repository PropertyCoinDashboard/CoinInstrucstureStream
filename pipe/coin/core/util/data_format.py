"""
Coin present data format architecture
"""

from __future__ import annotations
from typing import Any, Union
from decimal import Decimal, ROUND_HALF_UP
from pydantic import BaseModel, field_validator, ValidationError


class CoinMarket(BaseModel):
    """
    Subject:
        - coin_preset_price_total_schema \n
    Returns:
        - pydantic in JSON transformation \n
        >>> {
                "timestamp": 1689633864,
                "upbit": {
                    "name": "upbit-ETH",
                    "coin_symbol": "BTC",
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

    timestamp: int
    upbit: Union[CoinMarketData, bool]
    bithumb: Union[CoinMarketData, bool]
    coinone: Union[CoinMarketData, bool]
    korbit: Union[CoinMarketData, bool]
    gopax: Union[CoinMarketData, bool]

    def __init__(self, **data: CoinMarket) -> None:
        # 우선 timestamp 추출
        timestamp = data.pop("timestamp", None)

        # 거래소 데이터 검증 및 할당
        exchange_data: dict[int, Union[CoinMarketData, bool]] = {
            key: self.validate_exchange_data(value) for key, value in data.items()
        }
        # 합쳐진 데이터를 사용하여 부모 클래스 초기화
        super().__init__(timestamp=timestamp, **exchange_data)

    @staticmethod
    def validate_exchange_data(value: Any) -> Union[CoinMarketData, bool]:
        try:
            return CoinMarketData.model_validate(value)
        except ValidationError:
            return False


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

    @field_validator("*")
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
    coin_symbol: str
    data: PriceData

    @classmethod
    def _create_price_data(cls, api: dict[str, str], data: list[str]) -> PriceData:
        try:
            return PriceData(
                opening_price=Decimal(api[data[0]]),
                max_price=Decimal(api[data[2]]),
                min_price=Decimal(api[data[3]]),
                trade_price=Decimal(api[data[1]]),
                prev_closing_price=Decimal(api[data[4]]),
                acc_trade_volume_24h=Decimal(api[data[5]]),
            )
        except KeyError as e:
            raise KeyError(f"Key {e} not found in API response") from e

    @classmethod
    def from_api(
        cls,
        market: str,
        coin_symbol: str,
        api: dict[str, Any],
        data: list[str],
    ) -> CoinMarketData:
        """다음과 같은 dictionary를 만들기 위한 pydantic json model architecture
        >>>  {
            "market": "upbit-BTC",
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
            coin_symbol (str): 심볼
            api (Mapping[str, Any]): 거래소 API
            data (list[str, str, str, str, str, str]): 사용할 파라미터 \n
        Returns:
            CoinMarketData: _description_
        """
        price_data: PriceData = cls._create_price_data(api=api, data=data)
        return cls(
            market=market,
            coin_symbol=coin_symbol,
            data=price_data,
        )
