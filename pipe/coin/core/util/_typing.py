# market JSON format 값
# pipe -> ocin -> core -> config -> rest or socket.json 확인 가능
from typing import Union, TypedDict
from decimal import Decimal
from dataclasses import dataclass

Timestamp = Union[str, int, float]


class ExchangeRestConfig(TypedDict):
    parameter: list[str]


class ExchangeSocketConfig(TypedDict):
    parameter: list[Union[str, float]]


ExchangeRestDataTypeHints = dict[str, ExchangeRestConfig]
ExchangeSocketDataTypeHints = dict[str, ExchangeSocketConfig]


@dataclass
class ExchangeData:
    name: str
    coin_symbol: str
    data: dict[str, Decimal]


@dataclass
class TotalCoinMarketData:
    """
    모든 마켓 타입 스키마 제작
    -  동일한 컬럼 값의 대한 타입 시스템
    - dict[str, Union[str, int, dict[str, Decimal]]]
    """

    time: int
    upbit: Union[ExchangeData, bool]
    bithumb: Union[ExchangeData, bool]
    coinone: Union[ExchangeData, bool]
    korbit: Union[ExchangeData, bool]
    gopax: Union[ExchangeData, bool]
