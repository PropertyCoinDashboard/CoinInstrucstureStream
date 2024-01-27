"""
코인 정보 추상화
"""
import uuid
from typing import Any
from datetime import datetime, timezone

from coin.core.abstract.api_abstract_socket import CoinAbstactSocket


class UpbitSocket(CoinAbstactSocket):
    """UPBIT

    Args:
        CoinSocket (_type_): abstruct class
    """

    def __init__(self) -> None:
        super().__init__(market="upbit")
        self.__upbit_websocket = "wss://api.upbit.com/websocket/v1"

    def get_socket_parameter(self, symbol: str) -> list[dict[str, Any]]:
        return [
            {"ticket": str(uuid.uuid4())},
            {
                "type": "ticker",
                "codes": [f"KRW-{symbol.upper()}"],
                "isOnlyRealtime": True,
            },
        ]

    async def get_present_websocket(self, symbol: str) -> None:
        from coin.streaming.coin_socket_interaction import (
            WebsocketConnectionManager as WCM,
        )

        return await WCM().websocket_to_json(
            uri=self.__upbit_websocket,
            subscribe_fmt=self.get_socket_parameter(symbol=symbol),
            symbol=symbol,
        )


class BithumbSocket(CoinAbstactSocket):
    """Bithumb

    Args:
        CoinSocket (_type_): abstruct class
    """

    def __init__(self) -> None:
        super().__init__(market="bithum")
        self.__bithumb_websocket = "wss://pubwss.bithumb.com/pub/ws"

    def get_socket_parameter(self, symbol: str) -> dict[str, Any]:
        return {
            "type": "ticker",
            "symbols": [f"{symbol.upper()}_KRW"],
            "tickTypes": ["MID"],
        }

    async def get_present_websocket(self, symbol: str) -> None:
        from coin.streaming.coin_socket_interaction import (
            WebsocketConnectionManager as WCM,
        )

        return await WCM().websocket_to_json(
            uri=self.__bithumb_websocket,
            subscribe_fmt=self.get_socket_parameter(symbol=symbol),
            symbol=symbol,
        )


class KorbitSocket(CoinAbstactSocket):
    """Korbit

    Args:
        CoinSocket (_type_): abstruct class
    """

    def __init__(self) -> None:
        super().__init__(market="korbit")
        self.__korbit_websocket = "wss://ws.korbit.co.kr/v1/user/push"

    def get_socket_parameter(self, symbol: str) -> dict[str, Any]:
        return {
            "accessToken": None,
            "timestamp": int(datetime.now(timezone.utc).timestamp()),
            "event": "korbit:subscribe",
            "data": {"channels": [f"ticker:{symbol.lower()}_krw"]},
        }

    async def get_present_websocket(self, symbol: str) -> None:
        from coin.streaming.coin_socket_interaction import (
            WebsocketConnectionManager as WCM,
        )

        return await WCM().websocket_to_json(
            uri=self.__korbit_websocket,
            subscribe_fmt=self.get_socket_parameter(symbol=symbol),
            symbol=symbol,
        )


class CoinoneSocket(CoinAbstactSocket):
    """Coinone

    Args:
        CoinSocket (_type_): abstruct class
        소켓 미지원
    """

    pass
