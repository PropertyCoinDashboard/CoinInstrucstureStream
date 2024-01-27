# market JSON format 값
# pipe -> ocin -> core -> config -> rest or socket.json 확인 가능
from typing import Union, TypedDict

Timestamp = Union[str, int, float]


class ExchangeRestConfig(TypedDict):
    timestamp: Timestamp
    parameter: list[str]


class ExchangeSocketConfig(TypedDict):
    timestamp: Union[str, int, float]
    parameter: list[Union[str, float]]


ExchangeRestDataTypeHints = dict[str, ExchangeRestConfig]
ExchangeSocketDataTypeHints = dict[str, ExchangeSocketConfig]
