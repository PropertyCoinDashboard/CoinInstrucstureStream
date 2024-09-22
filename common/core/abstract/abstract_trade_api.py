"""대한민국 거래소 그리고 해외거래소 통합 추상 클래스"""

from typing import Any
from abc import abstractmethod, ABC


# Rest
class AbstractExchangeRestClient(ABC):
    @abstractmethod
    async def get_coin_all_info_price(self, coin_name: str) -> dict[str, Any]:
        """
        Subject:
            - 코인 인덱스 가격 정보 \n
        Parameter:
            - coin_name (str) : 코인이름\n
        Returns:
            - market 형식
        """
        raise NotImplementedError()


# Socket
class AbstractExchangeSocketClient(ABC):
    @abstractmethod
    async def get_present_websocket(self, symbol: str) -> None:
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
