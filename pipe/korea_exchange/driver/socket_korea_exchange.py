"""
코인 정보 추상화
"""

import uuid
from common.utils.other_utils import get_symbol_collect_url
from common.core.abstract import AbstractExchangeSocketClient
from common.core.types import (
    UpBithumbSocketParmater,
    CoinoneSocketParamter,
)


def upbithumb_socket_parameter(symbol: str) -> UpBithumbSocketParmater:
    return [
        {"ticket": str(uuid.uuid4())},
        {
            "type": "ticker",
            "codes": [f"KRW-{symbol.upper()}"],
            "isOnlyRealtime": True,
        },
    ]


class UpbitSocket(AbstractExchangeSocketClient):
    def __init__(self) -> None:
        self._websocket = get_symbol_collect_url("upbit", "socket")

    async def get_present_websocket(self, symbol: str) -> None:
        from korea_exchange.websocket_client import WebsocketConnectionManager as WCM

        return await WCM().websocket_to_json(
            uri=self._websocket,
            subs_fmt=upbithumb_socket_parameter(symbol=symbol),
            symbol=symbol,
        )


class BithumbSocket(AbstractExchangeSocketClient):
    def __init__(self) -> None:
        self._websocket = get_symbol_collect_url("bithumb", "socket")

    async def get_present_websocket(self, symbol: str) -> None:
        from korea_exchange.websocket_client import WebsocketConnectionManager as WCM

        return await WCM().websocket_to_json(
            uri=self._websocket,
            subs_fmt=upbithumb_socket_parameter(symbol=symbol),
            symbol=symbol,
        )


class CoinoneSocket(AbstractExchangeSocketClient):
    def __init__(self) -> None:
        self._websocket = get_symbol_collect_url("coinone", "socket")

    def get_socket_parameter(self, symbol: str) -> CoinoneSocketParamter:
        return {
            "request_type": "SUBSCRIBE",
            "channel": "TICKER",
            "topic": {"quote_currency": "KRW", "target_currency": f"{symbol.upper()}"},
        }

    async def get_present_websocket(self, symbol: str) -> None:
        from korea_exchange.websocket_client import WebsocketConnectionManager as WCM

        return await WCM().websocket_to_json(
            uri=self._websocket,
            subs_fmt=self.get_socket_parameter(symbol=symbol),
            symbol=symbol,
        )
