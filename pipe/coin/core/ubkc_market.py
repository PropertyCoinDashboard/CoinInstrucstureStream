"""
코인 정보 추상화
"""

import asyncio
import uuid
from typing import Any, Coroutine
from datetime import datetime, timezone

from coin.core.util.util_func import async_source_request, get_symbol_collect_url
from coin.core.abstract.ubkc_market_abstract import CoinSocketAndRestAbstract


class UpbitRestAndSocket(CoinSocketAndRestAbstract):
    """UPBIT

    Args:
        CoinRest (_type_): abstruct class
    """

    def __init__(self) -> None:
        self._websocket = get_symbol_collect_url("upbit", "socket")
        self._rest = get_symbol_collect_url("upbit", "rest")

    async def get_socket_parameter(
        self, symbol: str
    ) -> Coroutine[Any, Any, Coroutine[Any, Any, list[dict[str, Any]]]]:
        return [
            {"ticket": str(uuid.uuid4())},
            {
                "type": "ticker",
                "codes": [f"KRW-{symbol.upper()}"],
                "isOnlySnapshot": True,
            },
        ]

    async def get_present_websocket(self, symbol: str) -> Coroutine[Any, Any, None]:
        from coin.core.coin_socket_interaction import WebsocketConnectionManager as WCM

        return await WCM().websocket_to_json(
            uri=self._websocket,
            subscribe_fmt=await self.get_socket_parameter(symbol=symbol),
            symbol=symbol,
        )

    async def get_coin_all_info_price(self, coin_name: str) -> dict[str, Any]:
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
        data = await async_source_request(
            f"{self._rest}/ticker?markets=KRW-{coin_name.upper()}"
        )
        return data[0]


class BithumbRestAndSocket(CoinSocketAndRestAbstract):
    """Bithumb

    Args:
        CoinRest (_type_): abstruct class
    """

    def __init__(self) -> None:
        self._websocket = get_symbol_collect_url("bithumb", "socket")
        self._rest = get_symbol_collect_url("bithumb", "rest")

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
            uri=self._websocket,
            subscribe_fmt=await self.get_socket_parameter(symbol=symbol),
            symbol=symbol,
        )

    async def get_coin_all_info_price(self, coin_name: str) -> dict[str, Any]:
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
        data = await async_source_request(
            f"{self._rest}/ticker/{coin_name.upper()}_KRW"
        )
        return data["data"]


class CoinoneRestAndSocket(CoinSocketAndRestAbstract):
    """Coinone

    Args:
        CoinRest (_type_): abstruct class
    """

    def __init__(self) -> None:
        self._websocket = get_symbol_collect_url("coinone", "socket")
        self._rest = get_symbol_collect_url("coinone", "rest")

    async def get_socket_parameter(self, symbol: str) -> dict[str, str, dict[str, str]]:
        return {
            "request_type": "SUBSCRIBE",
            "channel": "TICKER",
            "topic": {"quote_currency": "KRW", "target_currency": f"{symbol}"},
        }

    async def get_present_websocket(self, symbol: str) -> None:
        from core.coin_socket_interaction import WebsocketConnectionManager as WCM

        return await WCM().websocket_to_json(
            uri=self._websocket,
            subscribe_fmt=await self.get_socket_parameter(symbol=symbol),
            symbol=symbol,
        )

    async def get_coin_all_info_price(self, coin_name: str) -> dict[str, Any]:
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
        data = await async_source_request(
            f"{self._rest}/ticker_new/KRW/{coin_name.upper()}?additional_data=true"
        )
        return data["tickers"][0]


class KorbitRestAndSocket(CoinSocketAndRestAbstract):
    """Korbit

    Args:
        CoinRest (_type_): abstruct class
    """

    def __init__(self) -> None:
        self._websocket = get_symbol_collect_url("korbit", "socket")
        self._rest = get_symbol_collect_url("korbit", "rest")

    async def get_socket_parameter(
        self, symbol: str
    ) -> Coroutine[Any, Any, list[dict[str, Any]]]:
        return {
            "accessToken": None,
            "timestamp": int(datetime.now(timezone.utc).timestamp()),
            "event": "korbit:subscribe",
            "data": {"channels": [f"ticker:{symbol.lower()}_krw"]},
        }

    async def get_present_websocket(self, symbol: str) -> None:
        from core.coin_socket_interaction import WebsocketConnectionManager as WCM

        return await WCM().websocket_to_json(
            uri=self._websocket,
            subscribe_fmt=await self.get_socket_parameter(symbol=symbol),
            symbol=symbol,
        )

    async def get_coin_all_info_price(self, coin_name: str) -> dict[str, Any]:
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
        return await async_source_request(
            f"{self._rest}/ticker/detailed?currency_pair={coin_name.lower()}_krw"
        )


class GoPaxRestAndSocket(CoinSocketAndRestAbstract):
    """Gopax

    Args:
        CoinRest (_type_): abstruct class
    """

    def __init__(self) -> None:
        self._websocket = get_symbol_collect_url("gopax", "socket")
        self._rest = get_symbol_collect_url("gopax", "rest")

    async def get_socket_parameter(
        self, symbol: str
    ) -> Coroutine[Any, Any, list[dict[str, Any]]]:
        pass

    async def get_present_websocket(self, symbol: str) -> Coroutine[Any, Any, None]:
        pass

    async def get_coin_all_info_type(self, coin_name: str, endpoint: str) -> dict[str]:
        return await async_source_request(
            f"{self._rest}/trading-pairs/{coin_name.upper()}-KRW/{endpoint}"
        )

    async def get_coin_all_info_price(self, coin_name: str) -> dict[str, int]:
        # fmt: off
        async def date_prepros(process: dict[str, int], element: set[str]) -> dict[str, int]:
            return {key: value for key, value in process.items() if key in element}

        price_data = self.get_coin_all_info_type(coin_name, "stats")
        ticker_task = self.get_coin_all_info_type(coin_name, "ticker")
        price, ticker = await asyncio.gather(price_data, ticker_task)

        relevant_keys = {"open", "close", "price", "bid", "ask", "volume"}
        stats = await date_prepros(price, relevant_keys)
        present = await date_prepros(ticker, relevant_keys)
        stats.update(present)

        c = ["close", "price", "bid", "ask", "open", "volume"]
        return dict(sorted(stats.items(), key=lambda n: c.index(n[0])))
