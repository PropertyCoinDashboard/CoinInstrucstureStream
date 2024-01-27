"""
코인 정보 추상화
"""
from typing import Any
from collections import Counter

from coin.core.util.util_func import header_to_json

from coin.core.abstract.api_abstract_rest import CoinAbstactRest
from coin.core.util.data_format import CoinSymbol, CoinNameAndSymbol


class UpbitRest(CoinAbstactRest):
    """UPBIT

    Args:
        CoinRest (_type_): abstruct class
    """

    def __init__(self) -> None:
        super().__init__(market="upbit")
        self.upbit_coin_list: list[dict[str, str]] = header_to_json(
            url=f"{self.url}/market/all?isDetails=true"
        )

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


class BithumbRest(CoinAbstactRest):
    """Bithumb

    Args:
        CoinRest (_type_): abstruct class
    """

    def __init__(self) -> None:
        super().__init__(market="bithum")
        self.__bithumb_coin_list: dict[str, Any] = header_to_json(
            url=f"{self.url}/ticker/ALL_KRW"
        )

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
            for symbol in self.__bithumb_coin_list["data"]
        ][:-1]


class CoinoneRest(CoinAbstactRest):
    """Coinone

    Args:
        CoinRest (_type_): abstruct class
    """

    def __init__(self) -> None:
        super().__init__(market="coinone")
        self.__coinone_coin_list = header_to_json(url=f"{self.url}/currencies")

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


class KorbitRest(CoinAbstactRest):
    """Korbit

    Args:
        CoinRest (_type_): abstruct class
    """

    def __init__(self) -> None:
        super().__init__(market="korbit")
        self.__korbit_coin_list: dict[str, dict[str, Any]] = header_to_json(
            url=f"{self.url}/ticker/detailed/all"
        )

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


class CoinNameAndSymbolMatching:
    """
    coin_symbol: name extraction \n
    upbit 기준으로 작성함 korbit, bithumb은 미지원
    """

    def __init__(self) -> None:
        self.upbit = UpbitRest()
        self.bithumb = BithumbRest()
        self.korbit = KorbitRest()
        self.coinone = CoinoneRest()

    def __get_all_coin_symbols(self) -> list[str]:
        """
        Subject:
            - 코인 심볼 병합\n
        Returns:
            >>> list[str]: ["BTC"...]
        """
        data = self.upbit.get_coinsymbol_extraction()
        data.extend(self.bithumb.get_coinsymbol_extraction())
        data.extend(self.korbit.get_coinsymbol_extraction())
        data.extend(self.coinone.get_coinsymbol_extraction())

        return data

    def get_duplication_coinsymbols(self) -> list[str]:
        """
        Subject:
            - 중복 코인 추출\n
        Returns:
            >>> list[str]: ["BTC"...]
        """
        results: list[tuple[str, int]] = Counter(
            self.__get_all_coin_symbols()
        ).most_common()
        symbol_count: list[str] = [index for index, data in results if data == 4]

        return symbol_count

    def coin_symbol_name_extaction(self) -> list[dict[str, str]]:
        """
        Subject:
           - 중복 코인 추출 후 upbit coin_market_list 에서 정보 추출 \n
        Returns:
            >>> list[dict[str, str]]: [{"BTC": "비트코인"}]
        """
        upbit_symbol: list[dict[str, str]] = self.upbit.upbit_coin_list
        return [
            CoinNameAndSymbol(
                coin_symbol=upbit_s["market"].split("KRW-")[-1],
                korean_name=upbit_s["korean_name"],
            ).model_dump()
            for upbit_s in upbit_symbol
            if upbit_s["market"].split("KRW-")[-1] in self.get_duplication_coinsymbols()
        ]
