from typing import Any
from abc import abstractmethod, ABC
from coin.core.util.util_func import get_symbol_collect_url


class CoinSocketAndRestAbstract(ABC):
    def __init__(self, market: str) -> None:
        self.url: str = get_symbol_collect_url(market)

    @abstractmethod
    def get_socket_parameter() -> list[dict[str, Any]]:
        """
        Returns:
            list[dict[str, Any]]: 각 거래소 socket parameter
        """
        raise NotImplementedError()

    @abstractmethod
    async def get_present_websocket(symbol: str) -> None:
        """
        Subject:
            - 코인 현재가 실시간 \n
        Args:
            - uri (str): 소켓주소
            - subscribe_fmt (list[dict]): 인증파라미터 \n
            - symbol (str) : 심볼
        Returns:
            - 무한루프 \n
        """
        raise NotImplementedError()

    @abstractmethod
    def get_coin_all_info_price(self, coin_name: str) -> dict[str, Any]:
        """
        Subject:
            - 코인 인덱스 가격 정보 \n
        Parameter:
            - coin_name (str) : 코인이름\n
        Returns:
            - market 형식
        """
        raise NotImplementedError()

    @abstractmethod
    def get_coin_present_opening_price(self, coin_name: str) -> dict[str, Any]:
        """
        Subject:
            - 코인 인덱스 가격 정보 \n
        Parameter:
            - coin_name (str) : 코인이름\n
        Returns:
            - market 형식
        """
        raise NotImplementedError()

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
