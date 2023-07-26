import tracemalloc
from typing import Any
from pathlib import Path

from abc import ABCMeta, abstractmethod
from coin.core.market.util_func import get_symbol_collect_url

present_path = Path(__file__).parent.parent


class CoinSocketAndPullRequest(metaclass=ABCMeta):
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
    async def get_present_websocket(self) -> None:
        """
        Subject:
            - 코인 현재가 실시간 \n
        Args:
            uri (str): 소켓주소
            subscribe_fmt (list[dict]): 인증파라미터 \n
        Returns:
            - 무한루프 \n
        """

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


class CoinPresentPriceMarketPlace(metaclass=ABCMeta):
    def __init__(self) -> None:
        tracemalloc.start()

    @abstractmethod
    async def coin_present_architecture(self):
        raise NotImplementedError()
