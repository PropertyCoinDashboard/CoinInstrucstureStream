"""
코인 정보 추상화
"""
from typing import Any
from abc import ABCMeta, abstractmethod
from collections import Counter

from coin.core.config.util_func import get_symbol_collect_url, header_to_json
from coin.core.data_format import CoinSymbol, CoinNameAndSymbol


class CoinPullRequest(metaclass=ABCMeta):
    """
    Subject:
        - 공통 목록 추상클래스 [개발 순서 및 혼동 방지]
        - 가독성 측면 [유지보수성 관리] \n
    Args:
        - market : 거래소 이름
    Function:
        - get_coinsymbol_extraction
            - 코인 심볼 반환
        - get_coin_present_price
            - 각 코인별 가격 반환
    """

    def __init__(self, market: str) -> None:
        self.url: str = get_symbol_collect_url(market)

    @abstractmethod
    def get_coinsymbol_extraction(self) -> list[str]:
        """
        Subject:
            - 코인 심볼 추출 \n
        Input:
            - market API 형식 \n
        Returns:
            >>> list[str]: ["BTC", "ETH" ....]
        """
        raise NotImplementedError()

    @abstractmethod
    def get_coin_present_price(self, coin_name: str) -> dict[str, Any]:
        """
        Subject:
            - 코인 인덱스 가격 정보 \n
        Parameter:
            - coin_name (str) : 코인이름\n
        Returns:
            - market 형식
        """
        raise NotImplementedError()


class UpbitCoinPullRequest(CoinPullRequest):
    """UPBIT

    Args:
        CoinPullRequest (_type_): abstruct class
    """

    def __init__(self) -> None:
        super().__init__(market="upbit")
        self.upbit_coin_list: list[dict[str, str]] = header_to_json(
            url=f"{self.url}/market/all?isDetails=true"
        )

    def get_coinsymbol_extraction(self) -> list[str]:
        """
        Subject:
            - 코인 심볼 추출 \n
        Input:
            >>> {
                'market_warning': 'NONE',
                'market': 'KRW-BLUR',
                'korean_name': '블러',
                'english_name': 'Blur'
            } \n
        Returns:
            >>> list[str]: ["BTC", "ETH" ....]
        """
        return [
            CoinSymbol(coin_symbol=symbol["market"].split("-")[-1]).coin_symbol
            for symbol in self.upbit_coin_list
            if symbol["market"].startswith("KRW-")
        ]

    def get_coin_present_price(self, coin_name: str) -> dict[str, Any]:
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
        return header_to_json(f"{self.url}/ticker?markets=KRW-{coin_name.upper()}")[0]


class BithumbCoinPullRequest(CoinPullRequest):
    """Bithumb

    Args:
        CoinPullRequest (_type_): abstruct class
    """

    def __init__(self) -> None:
        super().__init__(market="bithum")
        self.__bithum_coin_list: dict[str, Any] = header_to_json(
            url=f"{self.url}/ticker/ALL_KRW"
        )

    def get_coinsymbol_extraction(self) -> list[str]:
        """
        Subject:
            - 코인 심볼 추출 \n
        Input:
            >>> {
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
            >>> list[str]: ["BTC", "ETH" ....]
        """
        return [
            CoinSymbol(coin_symbol=symbol).coin_symbol
            for symbol in self.__bithum_coin_list["data"]
        ][:-1]

    def get_coin_present_price(self, coin_name: str) -> dict[str, Any]:
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
        return header_to_json(f"{self.url}/ticker/{coin_name.upper()}_KRW")["data"]


class CoinoneCoinPullRequest(CoinPullRequest):
    def __init__(self) -> None:
        super().__init__(market="coinone")
        self.__coinone_coin_list = header_to_json(url=f"{self.url}/currencies")

    def get_coinsymbol_extraction(self) -> list[str]:
        """
        Subject:
            - 코인 심볼 추출 \n
        Input:
           >>> {
                "name": "Bitcoin",
                "symbol": "BTC",
                "deposit_status": "normal",
                "withdraw_status": "normal"
                ...
            }
        Returns:
            >>> list[str]: ["BTC", "ETH" ....]
        """
        return [
            CoinSymbol(coin_symbol=symbol["symbol"]).coin_symbol
            for symbol in self.__coinone_coin_list["currencies"][0]
        ]

    def get_coin_present_price(self, coin_name: str) -> dict[str, Any]:
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
            f"{self.url}/ticker_new/KRW/{coin_name.upper()}?additional_data=true"
        )["tickers"][0]


class KorbitCoinPullRequest(CoinPullRequest):
    """Korbit

    Args:
        CoinPullRequest (_type_): abstruct class
    """

    def __init__(self) -> None:
        super().__init__(market="korbit")
        self.__korbit_coin_list: dict[str, dict[str, Any]] = header_to_json(
            url=f"{self.url}/ticker/detailed/all"
        )

    def get_coinsymbol_extraction(self) -> list[str]:
        """
        Subject:
            - 코인 심볼 추출 \n
        Input:
           >>> {
                "bch_krw": {
                    "timestamp": 1559285555322,
                    "last": "513000",
                    "open": "523900",
                    ...
                }
            } \n
        Returns:
            >>> list[str]: ["BTC", "ETH" ....]
        """
        return [
            CoinSymbol(coin_symbol=symbol.split("_")[0].upper()).coin_symbol
            for symbol in self.__korbit_coin_list
        ]

    def get_coin_present_price(self, coin_name: str) -> dict[str, Any]:
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
            f"{self.url}/ticker/detailed?currency_pair={coin_name.lower()}_krw"
        )


class CoinNameAndSymbolMatching:
    """
    coin_symbol: name extraction \n
    upbit 기준으로 작성함 korbit, bithumb은 미지원
    """

    def __init__(self) -> None:
        self.__upbit = UpbitCoinPullRequest()
        self.__bithumb = BithumbCoinPullRequest()
        self.__korbit = KorbitCoinPullRequest()
        self.__coinone = CoinoneCoinPullRequest()

        self.__all_coin_symbols = self.__get_all_coin_symbols()
        self.__duplication_coinsymbols = self.__get_duplication_coinsymbols()

    def __get_all_coin_symbols(self) -> list[str]:
        """
        Subject:
            - 코인 심볼 병합\n
        Returns:
            >>> list[str]: ["BTC"...]
        """
        data = self.__upbit.get_coinsymbol_extraction()
        data.extend(self.__bithumb.get_coinsymbol_extraction())
        data.extend(self.__korbit.get_coinsymbol_extraction())
        data.extend(self.__coinone.get_coinsymbol_extraction())

        return data

    def __get_duplication_coinsymbols(self) -> list[str]:
        """
        Subject:
            - 중복 코인 추출\n
        Returns:
            >>> list[str]: ["BTC"...]
        """
        results: list[tuple[str, int]] = Counter(self.__all_coin_symbols).most_common()
        symbol_count: list[str] = [index for index, data in results if data == 4]

        return symbol_count

    def coin_symbol_name_extaction(self) -> list[dict[str, str]]:
        """
        Subject:
           - 중복 코인 추출 후 upbit coin_market_list 에서 정보 추출 \n
        Returns:
            >>> list[dict[str, str]]: [{"BTC": "비트코인"}]
        """
        upbit_symbol: list[dict[str, str]] = self.__upbit.upbit_coin_list
        symbol_name = [
            CoinNameAndSymbol(
                coin_symbol=upbit_s["market"].split("KRW-")[-1],
                korean_name=upbit_s["korean_name"],
            ).model_dump()
            for upbit_s in upbit_symbol
            if upbit_s["market"].split("KRW-")[-1] in self.__duplication_coinsymbols
        ]

        return symbol_name
