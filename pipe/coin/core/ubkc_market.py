"""
코인 정보 추상화
"""

import uuid
from typing import Any, Coroutine
from datetime import datetime, timezone

from coin.core.util.util_func import header_to_json, get_symbol_collect_url
from coin.core.abstract.ubkc_market_abstract import CoinSocketAndRestAbstract


class UpbitRestAndSocket(CoinSocketAndRestAbstract):
    """UPBIT

    Args:
        CoinRest (_type_): abstruct class
    """

    def __init__(self) -> None:
        self.__websocket = get_symbol_collect_url("upbit", "socket")
        self.__rest = get_symbol_collect_url("upbit", "rest")

    async def get_socket_parameter(
        self, symbol: str
    ) -> Coroutine[Any, Any, Coroutine[Any, Any, list[dict[str, Any]]]]:
        return [
            {"ticket": str(uuid.uuid4())},
            {
                "type": "ticker",
                "codes": [f"KRW-{symbol.upper()}"],
                "isOnlyRealtime": True,
            },
        ]

    async def get_present_websocket(self, symbol: str) -> Coroutine[Any, Any, None]:
        from coin.core.coin_socket_interaction import WebsocketConnectionManager as WCM

        return await WCM().websocket_to_json(
            uri=self.__websocket,
            subscribe_fmt=await self.get_socket_parameter(symbol=symbol),
            symbol=symbol,
        )

    def get_coin_all_info_price(self, coin_name: str) -> dict[str, Any]:
        """
        Subject:
            - upbit 코인 현재가\n
        Parameter:
            - coin_name (str) : 코인이름\n
        Returns:
            >>>  {
                'market': 'KRW-BTC',
                'trade_date': '20230717',
                'trade_time': '090305',
                ...
            }
        """
        return header_to_json(f"{self.__rest}/ticker?markets=KRW-{coin_name.upper()}")[
            0
        ]


class BithumbRestAndSocket(CoinSocketAndRestAbstract):
    """Bithumb

    Args:
        CoinRest (_type_): abstruct class
    """

    def __init__(self) -> None:
        self.__websocket = get_symbol_collect_url("bithumb", "socket")
        self.__rest = get_symbol_collect_url("bithumb", "rest")

    async def get_socket_parameter(
        self, symbol: str
    ) -> Coroutine[Any, Any, list[dict[str, Any]]]:
        return {
            "type": "ticker",
            "symbols": [f"{symbol.upper()}_KRW"],
            "tickTypes": ["MID"],
        }

    async def get_present_websocket(self, symbol: str) -> Coroutine[Any, Any, None]:
        from coin.core.coin_socket_interaction import WebsocketConnectionManager as WCM

        return await WCM().websocket_to_json(
            uri=self.__websocket,
            subscribe_fmt=await self.get_socket_parameter(symbol=symbol),
            symbol=symbol,
        )

    def get_coin_all_info_price(self, coin_name: str) -> dict[str, Any]:
        """
        Subject:
            - bithum 코인 현재가\n
        Parameter:
            - coin_name (str) : 코인이름\n
        Returns:
            >>> {
                'opening_price': '39067000',
                'closing_price': '38770000',
                'min_price': '38672000',
                'max_price': '39085000',
                ...
            }
        """
        return header_to_json(f"{self.__rest}/ticker/{coin_name.upper()}_KRW")["data"]


class CoinoneRestAndSocket(CoinSocketAndRestAbstract):
    """Coinone

    Args:
        CoinRest (_type_): abstruct class
    """

    def __init__(self) -> None:
        self.__websocket = get_symbol_collect_url("coinone", "socket")
        self.__rest = get_symbol_collect_url("coinone", "rest")

    async def get_socket_parameter(self, symbol: str) -> dict[str, str, dict[str, str]]:
        return {
            "request_type": "SUBSCRIBE",
            "channel": "TICKER",
            "topic": {"quote_currency": "KRW", "target_currency": f"{symbol}"},
        }

    async def get_present_websocket(self, symbol: str) -> Coroutine[Any, Any, None]:
        from coin.core.coin_socket_interaction import WebsocketConnectionManager as WCM

        return await WCM().websocket_to_json(
            uri=self.__websocket,
            subscribe_fmt=await self.get_socket_parameter(symbol=symbol),
            symbol=symbol,
        )

    def get_coin_all_info_price(self, coin_name: str) -> dict[str, Any]:
        """
        Subject:
            - coinone 코인 현재가 추출\n
        Parameter:
            - coin_name (str) : 코인이름\n
        Returns:
            >>> {
                "quote_currency": "KRW",
                "target_currency": "BTC",
                "timestamp": 1499341142000,
                "high": "3845000.0",
                "low": "3819000.0",
                ...
            }
        """
        return header_to_json(
            f"{self.__rest}/ticker_new/KRW/{coin_name.upper()}?additional_data=true"
        )["tickers"][0]


class KorbitRestAndSocket(CoinSocketAndRestAbstract):
    """Korbit

    Args:
        CoinRest (_type_): abstruct class
    """

    def __init__(self) -> None:
        self.__websocket = get_symbol_collect_url("korbit", "socket")
        self.__rest = get_symbol_collect_url("korbit", "rest")

    async def get_socket_parameter(
        self, symbol: str
    ) -> Coroutine[Any, Any, list[dict[str, Any]]]:
        return {
            "accessToken": None,
            "timestamp": int(datetime.now(timezone.utc).timestamp()),
            "event": "korbit:subscribe",
            "data": {"channels": [f"ticker:{symbol.lower()}_krw"]},
        }

    async def get_present_websocket(self, symbol: str) -> Coroutine[Any, Any, None]:
        from coin.core.coin_socket_interaction import WebsocketConnectionManager as WCM

        return await WCM().websocket_to_json(
            uri=self.__websocket,
            subscribe_fmt=await self.get_socket_parameter(symbol=symbol),
            symbol=symbol,
        )

    def get_coin_all_info_price(self, coin_name: str) -> dict[str, Any]:
        """
        Subject:
            - korbit 코인 현재가 추출\n
        Parameter:
            - coin_name (str) : 코인이름\n
        Returns:
            >>> {
                "timestamp": 1689595134649,
                "last": "38809000",
                "open": "38932000",
                "bid": "38808000",
                ...
            }
        """
        return header_to_json(
            f"{self.__rest}/ticker/detailed?currency_pair={coin_name.lower()}_krw"
        )


class GoPaxRestAndSocket(CoinSocketAndRestAbstract):
    """Gopax

    Args:
        CoinRest (_type_): abstruct class
    """

    def __init__(self) -> None:
        self.__websocket = get_symbol_collect_url("gopax", "socket")
        self.__rest = get_symbol_collect_url("gopax", "rest")

    async def get_socket_parameter(
        self, symbol: str
    ) -> Coroutine[Any, Any, list[dict[str, Any]]]:
        pass

    async def get_present_websocket(self, symbol: str) -> Coroutine[Any, Any, None]:
        pass

    def get_coin_all_info_price(self, coin_name: str) -> dict[str, Any]:
        """
        Subject:
            - gopax 코인 현재가 추출\n
        Parameter:
            - coin_name (str) : 코인이름\n
        Returns:
            >>> {
                    "price": 15393000,                   # 오더북 상의 현재 가격
                    "ask": 15397000,                     # 오더북 상의 현재 가장 낮은 매도 가격
                    "askVolume": 0.56,                   # 오더북 상의 현재 가장 낮은 매도 가격의 수량
                    "bid": 15393000,                     # 오더북 상의 현재 가장 높은 매수 가격
                    "bidVolume": 1.9513,                 # 오더북 상의 현재 가장 높은 매수 가격의 수량
                    "volume": 487.43035427,              # 최근 24시간 누적 거래량 (base 자산 단위로 이 예시에서는 BTC)
                    "quoteVolume": 7319576689.34135,     # 최근 24시간 누적 거래량 (quote 자산 단위로 이 예시에서는 KRW)
                    "time": "2020-10-28T02:05:55.958Z"   # 티커 최근 갱신 시간
                    }
        """
        return header_to_json(
            f"{self.__rest}/trading-pairs/{coin_name.upper()}-KRW/ticker"
        )
