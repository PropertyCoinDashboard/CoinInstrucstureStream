import uuid
from typing import Union, TypedDict, NewType
from decimal import Decimal
from dataclasses import dataclass


ExchangeResponseData = dict[str, Union[str, int, float]]

TIMESTAMP = NewType("TIMESTAMP", int)


class SocketJsonType(TypedDict):
    timestamp: TIMESTAMP
    parameter: list[str]


class RestJsonType(TypedDict):
    parameter: list[str]


class MarketRequestJsonType(TypedDict):
    market: SocketJsonType | RestJsonType


KoreaMarketsLoadJson = MarketRequestJsonType

PriceData = dict[str, Decimal]


@dataclass
class ExchangeData:
    name: str
    coin_symbol: str
    data: dict[str, Decimal]


@dataclass
class KoreaCoinMarketData:
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


UUID = NewType("UUID", str(uuid.uuid4()))


class TicketUUID(TypedDict):
    ticket: UUID


class TickerWebSocketRequest(TypedDict):
    type: str
    codes: list[str]
    stream_type: bool


UpBithumbSocketParmater = list[TicketUUID, TickerWebSocketRequest]
CoinoneSocketParamter = dict[str, str | dict[str, str]]

SubScribeFormat = UpBithumbSocketParmater | CoinoneSocketParamter
