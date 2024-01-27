from typing import Any
from abc import abstractmethod, ABC
from coin.core.util.util_func import get_symbol_collect_url


class CoinAbstactSocket(ABC):
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
