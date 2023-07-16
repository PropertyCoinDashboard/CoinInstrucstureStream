from typing import Any
from abc import ABC, abstractmethod
from data_format import CoinSymbol
from properties import get_symbol_collect_url, header_to_json


class CoinFullRequest(ABC):
    """
    Subject:
        - 공통 목록 추상클래스 [개발 순서 및 혼동 방지]
        - 가독성 측면 [유지보수성 관리]

    Args:
        - market : 거래소 이름
        - symbol_collect : 코인 심볼 뽑아낼때 쓰는 URL
    """

    def __init__(self, market: str) -> None:
        self.market = market
        self.symbol_collect: str = get_symbol_collect_url(self.market)

    @abstractmethod
    def coinsymbol_extraction(self) -> list[str]:
        """
        Subject:
            - 코인 심볼 추출

        Input:
            - market API 형식

        Returns:
            - list[str]: ["BTC", "ETH" ....]
        """
        pass


class UpBitCoinFullRequest(CoinFullRequest):
    def __init__(self) -> None:
        super().__init__(market="upbit")
        self.upbit_coin_list: list[dict[str, str]] = header_to_json(
            url=f"{self.symbol_collect}/market/all?isDetails=true"
        )

    def coinsymbol_extraction(self) -> list[str]:
        """
        Subject:
            - 코인 심볼 추출 \n
        Input:
            - {
                'market_warning': 'NONE',
                'market': 'KRW-BLUR',
                'korean_name': '블러',
                'english_name': 'Blur'
            } \n
        Returns:
            - list[str]: ["BTC", "ETH" ....]
        """
        return [
            CoinSymbol(coin_symbol=symbol["market"].split("-")[-1]).coin_symbol
            for symbol in self.upbit_coin_list
            if symbol["market"].startswith("KRW-")
        ]


class BithumbCoinFullRequest(CoinFullRequest):
    def __init__(self) -> None:
        super().__init__(market="bithum")
        self.bithum_coin_list: dict[str, Any] = header_to_json(
            url=f"{self.symbol_collect}/ticker/ALL_KRW"
        )

    def coinsymbol_extraction(self) -> list[str]:
        """
        Subject:
            - 코인 심볼 추출 \n
        Input:
            - {
                "status": "0000",
                "data": {
                    "BTC": {
                        "opening_price": "54353000",
                        "closing_price": "53768000",
                        "min_price": "53000000"
                        ...
                    }
                }
            } \n
        Returns:
            - list[str]: ["BTC", "ETH" ....]
        """
        return [
            CoinSymbol(coin_symbol=symbol).coin_symbol
            for symbol in self.bithum_coin_list["data"]
        ][:-1]


class KorbitCoinFullRequest(CoinFullRequest):
    def __init__(self) -> None:
        super().__init__(market="korbit")
        self.korbit_coin_list: dict[str, dict[str, Any]] = header_to_json(
            url=f"{self.symbol_collect}/ticker/detailed/all"
        )

    def coinsymbol_extraction(self):
        """
        Subject:
            - 코인 심볼 추출 \n
        Input:
           - {
                "bch_krw": {
                    "timestamp": 1559285555322,
                    "last": "513000",
                    "open": "523900",
                    ...
                }
            } \n
        Returns:
            - list[str]: ["BTC", "ETH" ....]
        """
        return [
            CoinSymbol(coin_symbol=symbol.split("_")[0].upper()).coin_symbol
            for symbol in self.korbit_coin_list
        ]
