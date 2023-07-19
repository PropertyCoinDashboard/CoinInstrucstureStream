from typing import Any
from abc import ABCMeta, abstractmethod
from schema.data_format import CoinSymbol
from setting.properties import get_symbol_collect_url, header_to_json


class CoinFullRequest(metaclass=ABCMeta):
    """
    Subject:
        - 공통 목록 추상클래스 [개발 순서 및 혼동 방지]
        - 가독성 측면 [유지보수성 관리] \n
    Args:
        - market : 거래소 이름
        - symbol_collect : 코인 심볼 뽑아낼때 쓰는 URL
    Function:
        - get_coinsymbol_extraction
        - get_coin_present_price
    """

    def __init__(self, market: str, coin_name: str) -> None:
        self.coin_name = coin_name
        self.url: str = get_symbol_collect_url(market)

    @abstractmethod
    def get_coinsymbol_extraction(self) -> list[str]:
        """
        Subject:
            - 코인 심볼 추출 \n
        Input:
            - market API 형식 \n
        Returns:
            - list[str]: ["BTC", "ETH" ....]
        """
        raise NotImplementedError()

    @abstractmethod
    def get_coin_present_price(self) -> dict[str, Any]:
        """
        Subject:
            - 코인 인덱스 가격 정보 \n
        Returns:
            - market 형식
        """
        raise NotImplementedError()


class UpBitCoinFullRequest(CoinFullRequest):
    def __init__(self, coin_name: str) -> None:
        super().__init__(coin_name=coin_name, market="upbit")
        self.upbit_coin_list: list[dict[str, str]] = header_to_json(
            url=f"{self.url}/market/all?isDetails=true"
        )
        self.upbit_coin_present_price = header_to_json(
            url=f"{self.url}/ticker?markets=KRW-{self.coin_name.upper()}"
        )

    def get_coinsymbol_extraction(self) -> list[str]:
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

    def get_coin_present_price(self) -> dict[str, Any]:
        """
        Subject:
            - upbit 코인 현재가\n
        Returns:
            -  {
                'market': 'KRW-BTC',
                'trade_date': '20230717',
                'trade_time': '090305',
                ...
            }
        """
        return self.upbit_coin_present_price[0]


class BithumbCoinFullRequest(CoinFullRequest):
    def __init__(self, coin_name: str) -> None:
        super().__init__(coin_name=coin_name, market="bithum")
        self.bithum_coin_list: dict[str, Any] = header_to_json(
            url=f"{self.url}/ticker/ALL_KRW"
        )
        self.bithum_present_price = header_to_json(
            url=f"{self.url}/ticker/{self.coin_name.upper()}_KRW"
        )

    def get_coinsymbol_extraction(self) -> list[str]:
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

    def get_coin_present_price(self) -> dict[str, Any]:
        """
        Subject:
            - bithum 코인 현재가\n
        Returns:
            - {
                'opening_price': '39067000',
                'closing_price': '38770000',
                'min_price': '38672000',
                'max_price': '39085000',
                ...
            }
        """
        return self.bithum_present_price["data"]


class KorbitCoinFullRequest(CoinFullRequest):
    def __init__(self, coin_name: str) -> None:
        super().__init__(coin_name=coin_name, market="korbit")
        self.korbit_coin_list: dict[str, dict[str, Any]] = header_to_json(
            url=f"{self.url}/ticker/detailed/all"
        )
        self.korbit_present_price = header_to_json(
            f"{self.url}/ticker/detailed?currency_pair={self.coin_name.lower()}_krw"
        )

    def get_coinsymbol_extraction(self) -> list[str]:
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

    def get_coin_present_price(self) -> dict[str, Any]:
        """
        Subject:
            - korbit 코인 현재가 추출\n
        Returns:
            - {
                "timestamp": 1689595134649,
                "last": "38809000",
                "open": "38932000",
                "bid": "38808000",
                ...
            }
        """
        return self.korbit_present_price
